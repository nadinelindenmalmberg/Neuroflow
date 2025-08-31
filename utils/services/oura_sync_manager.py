"""
OuraSyncManager - Handles automatic Oura data synchronization
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask_apscheduler import APScheduler
from models import db, User, SyncLog
from utils.services.oura_fetch_and_store import fetch_oura_data, flatten_oura_chunks, clean_data, store_oura_data

logger = logging.getLogger(__name__)

class OuraSyncManager:
    """Manages automatic Oura data synchronization"""
    
    def __init__(self, scheduler: APScheduler):
        self.scheduler = scheduler
        self.job_prefix = "oura_sync_user_"
    
    def schedule_user_sync(self, user_id: int, frequency: str) -> bool:
        """
        Schedule automatic sync for a user based on frequency
        
        Args:
            user_id: User ID to schedule sync for
            frequency: 'daily', 'weekly', or 'manual'
            
        Returns:
            bool: True if scheduled successfully, False otherwise
        """
        try:
            job_id = f"{self.job_prefix}{user_id}"
            
            # Remove existing job if it exists
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Don't schedule if frequency is manual
            if frequency == 'manual':
                return True
            
            # Calculate interval based on frequency
            if frequency == 'daily':
                trigger = 'interval'
                hours = 24
            elif frequency == 'weekly':
                trigger = 'interval'
                hours = 168  # 7 days
            else:
                logger.warning(f"Invalid frequency '{frequency}' for user {user_id}")
                return False
            
            # Add the job to scheduler
            self.scheduler.add_job(
                func=self.run_user_sync,
                trigger=trigger,
                hours=hours,
                id=job_id,
                args=[user_id],
                replace_existing=True,
                misfire_grace_time=3600  # 1 hour grace time for missed jobs
            )
            
            logger.info(f"Scheduled {frequency} sync for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule sync for user {user_id}: {str(e)}")
            return False
    
    def unschedule_user_sync(self, user_id: int) -> bool:
        """
        Remove scheduled sync for a user
        
        Args:
            user_id: User ID to unschedule
            
        Returns:
            bool: True if unscheduled successfully, False otherwise
        """
        try:
            job_id = f"{self.job_prefix}{user_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Unscheduled sync for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to unschedule sync for user {user_id}: {str(e)}")
            return False
    
    def run_user_sync(self, user_id: int) -> Dict[str, Any]:
        """
        Run automatic sync for a specific user
        
        Args:
            user_id: User ID to sync for
            
        Returns:
            Dict with sync results
        """
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return {"success": False, "error": "User not found"}
        
        if not user.oura_api_token:
            logger.error(f"No Oura token found for user {user_id}")
            return {"success": False, "error": "No Oura token found"}
        
        if not user.sync_enabled:
            logger.info(f"Automatic sync disabled for user {user_id}")
            return {"success": False, "error": "Automatic sync disabled"}
        
        # Calculate date range (last 7 days if no last sync, otherwise since last sync)
        if user.last_automatic_sync:
            start_date = user.last_automatic_sync.date()
        else:
            start_date = datetime.now().date() - timedelta(days=7)
        
        end_date = datetime.now().date()
        
        # Convert dates to strings for the fetch function
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Create sync log entry
        sync_log = SyncLog(
            user_id=user_id,
            sync_type='automatic',
            status='in_progress',
            start_date=start_date,
            end_date=end_date,
            started_at=datetime.utcnow()
        )
        db.session.add(sync_log)
        db.session.commit()
        
        try:
            logger.info(f"Starting automatic sync for user {user_id} from {start_date} to {end_date}")
            
            # Fetch and store data
            all_data = fetch_oura_data(user.oura_api_token, start_date_str, end_date_str)
            flattened = flatten_oura_chunks(all_data)
            cleaned = clean_data(flattened)
            store_oura_data(cleaned)
            
            # Count records imported
            records_imported = len(cleaned) if cleaned else 0
            
            # Update sync log with success
            sync_log.status = 'success'
            sync_log.records_imported = records_imported
            sync_log.completed_at = datetime.utcnow()
            
            # Update user's sync timestamps
            user.last_automatic_sync = datetime.utcnow()
            user.last_oura_sync = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Automatic sync completed for user {user_id}: {records_imported} records imported")
            
            return {
                "success": True,
                "records_imported": records_imported,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "sync_log_id": sync_log.id
            }
            
        except Exception as e:
            logger.error(f"Automatic sync failed for user {user_id}: {str(e)}")
            
            # Update sync log with failure
            sync_log.status = 'failed'
            sync_log.error_message = str(e)
            sync_log.completed_at = datetime.utcnow()
            db.session.commit()
            
            return {
                "success": False,
                "error": str(e),
                "sync_log_id": sync_log.id
            }
    
    def get_user_sync_status(self, user_id: int) -> Dict[str, Any]:
        """
        Get sync status for a user
        
        Args:
            user_id: User ID to get status for
            
        Returns:
            Dict with sync status information
        """
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        job_id = f"{self.job_prefix}{user_id}"
        job = self.scheduler.get_job(job_id)
        
        return {
            "user_id": user_id,
            "sync_enabled": user.sync_enabled,
            "sync_frequency": user.sync_frequency,
            "last_automatic_sync": user.last_automatic_sync.isoformat() if user.last_automatic_sync else None,
            "next_scheduled_sync": user.next_scheduled_sync.isoformat() if user.next_scheduled_sync else None,
            "job_scheduled": job is not None,
            "next_job_run": job.next_run_time.isoformat() if job and job.next_run_time else None
        }
    
    def update_user_sync_settings(self, user_id: int, sync_enabled: bool, frequency: str) -> bool:
        """
        Update sync settings for a user
        
        Args:
            user_id: User ID to update
            sync_enabled: Whether automatic sync is enabled
            frequency: Sync frequency ('manual', 'daily', 'weekly')
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Update user settings
            user.sync_enabled = sync_enabled
            user.sync_frequency = frequency
            
            # Schedule or unschedule based on settings
            if sync_enabled and frequency != 'manual':
                success = self.schedule_user_sync(user_id, frequency)
                if success:
                    # Calculate next scheduled sync
                    if frequency == 'daily':
                        user.next_scheduled_sync = datetime.utcnow() + timedelta(days=1)
                    elif frequency == 'weekly':
                        user.next_scheduled_sync = datetime.utcnow() + timedelta(weeks=1)
            else:
                success = self.unschedule_user_sync(user_id)
                user.next_scheduled_sync = None
            
            db.session.commit()
            return success
            
        except Exception as e:
            logger.error(f"Failed to update sync settings for user {user_id}: {str(e)}")
            db.session.rollback()
            return False 