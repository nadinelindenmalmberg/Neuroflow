"""
FitbitSyncManager - Handles automatic Fitbit data synchronization
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask_apscheduler import APScheduler
from models import db, User, SyncLog
from utils.services.fitbit_fetch_and_store import fetch_fitbit_data, clean_fitbit_data, store_fitbit_data
from utils.services.fitbit_oauth import get_fitbit_oauth

logger = logging.getLogger(__name__)

class FitbitSyncManager:
    """Manages automatic Fitbit data synchronization"""
    
    def __init__(self, scheduler: APScheduler):
        self.scheduler = scheduler
        self.job_prefix = "fitbit_sync_user_"
    
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
            self.unschedule_user_sync(user_id)
            
            # Schedule new job based on frequency
            if frequency == 'daily':
                self.scheduler.add_job(
                    id=job_id,
                    func=self.run_user_sync,
                    args=[user_id],
                    trigger='cron',
                    hour=6,  # 6 AM daily
                    minute=0,
                    replace_existing=True
                )
                logger.info(f"Scheduled daily Fitbit sync for user {user_id}")
                
            elif frequency == 'weekly':
                self.scheduler.add_job(
                    id=job_id,
                    func=self.run_user_sync,
                    args=[user_id],
                    trigger='cron',
                    day_of_week=0,  # Sunday
                    hour=6,
                    minute=0,
                    replace_existing=True
                )
                logger.info(f"Scheduled weekly Fitbit sync for user {user_id}")
                
            elif frequency == 'manual':
                # No automatic scheduling for manual
                logger.info(f"Manual sync mode for user {user_id} - no automatic scheduling")
                return True
                
            else:
                logger.error(f"Invalid sync frequency: {frequency}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling Fitbit sync for user {user_id}: {e}")
            return False
    
    def unschedule_user_sync(self, user_id: int) -> bool:
        """
        Remove scheduled sync for a user
        
        Args:
            user_id: User ID to unschedule
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            job_id = f"{self.job_prefix}{user_id}"
            
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Unscheduled Fitbit sync for user {user_id}")
                return True
            else:
                logger.info(f"No scheduled Fitbit sync found for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error unscheduling Fitbit sync for user {user_id}: {e}")
            return False
    
    def run_user_sync(self, user_id: int) -> Dict[str, Any]:
        """
        Run manual or automatic sync for a user
        
        Args:
            user_id: User ID to sync data for
            
        Returns:
            dict: Sync result with success status and details
        """
        try:
            # Get user from database
            user = User.query.get(user_id)
            if not user:
                return {
                    "success": False,
                    "error": f"User {user_id} not found"
                }
            
            # Check if user has Fitbit tokens
            if not user.fitbit_access_token:
                return {
                    "success": False,
                    "error": "No Fitbit access token found for user"
                }
            
            # Determine date range for sync
            if user.last_fitbit_sync:
                # Sync from last sync date to yesterday
                start_date = user.last_fitbit_sync.date() + timedelta(days=1)
            else:
                # First sync - get last 30 days
                start_date = datetime.now().date() - timedelta(days=30)
            
            end_date = datetime.now().date() - timedelta(days=1)  # Yesterday
            
            # Skip if start_date is in the future
            if start_date > end_date:
                return {
                    "success": True,
                    "message": "No new data to sync",
                    "records_imported": 0
                }
            
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
                logger.info(f"Starting Fitbit sync for user {user_id} from {start_date} to {end_date}")
                
                # Check if access token needs refresh
                access_token = user.fitbit_access_token
                if user.fitbit_token_expires_at and user.fitbit_token_expires_at <= datetime.utcnow():
                    logger.info(f"Refreshing expired Fitbit token for user {user_id}")
                    oauth = get_fitbit_oauth()
                    refresh_result = oauth.refresh_access_token(user.fitbit_refresh_token)
                    
                    if refresh_result['success']:
                        user.fitbit_access_token = refresh_result['access_token']
                        user.fitbit_refresh_token = refresh_result['refresh_token']
                        user.fitbit_token_expires_at = datetime.utcnow() + timedelta(seconds=refresh_result['expires_in'])
                        db.session.commit()
                        access_token = refresh_result['access_token']
                    else:
                        raise Exception(f"Failed to refresh token: {refresh_result['error']}")
                
                # Fetch and store data
                raw_data = fetch_fitbit_data(access_token, start_date_str, end_date_str)
                cleaned_data = clean_fitbit_data(raw_data)
                records_imported = store_fitbit_data(cleaned_data)
                
                # Update sync log with success
                sync_log.status = 'success'
                sync_log.records_imported = records_imported
                sync_log.completed_at = datetime.utcnow()
                
                # Update user's sync timestamps
                user.last_fitbit_sync = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"Fitbit sync completed for user {user_id}: {records_imported} records imported")
                
                return {
                    "success": True,
                    "records_imported": records_imported,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "sync_log_id": sync_log.id
                }
                
            except Exception as e:
                # Update sync log with failure
                sync_log.status = 'failed'
                sync_log.error_message = str(e)
                sync_log.completed_at = datetime.utcnow()
                db.session.commit()
                
                logger.error(f"Fitbit sync failed for user {user_id}: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "sync_log_id": sync_log.id
                }
                
        except Exception as e:
            logger.error(f"Error in Fitbit sync for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Sync error: {str(e)}"
            }
    
    def test_connection(self, user_id: int) -> Dict[str, Any]:
        """
        Test Fitbit connection for a user
        
        Args:
            user_id: User ID to test connection for
            
        Returns:
            dict: Test result with success status and details
        """
        try:
            user = User.query.get(user_id)
            if not user or not user.fitbit_access_token:
                return {
                    "success": False,
                    "error": "No Fitbit access token found"
                }
            
            # Test the connection
            from utils.services.fitbit_fetch_and_store import FitbitAPI
            fitbit = FitbitAPI(user.fitbit_access_token)
            is_valid, message = fitbit.test_connection()
            
            return {
                "success": is_valid,
                "message": message,
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Error testing Fitbit connection for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

