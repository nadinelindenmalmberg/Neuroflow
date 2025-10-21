"""
Fitbit Web API Integration
Handles fetching and storing data from Fitbit Web API
"""
import requests
import pandas as pd
from datetime import datetime, timedelta, date
from models import db, Graph, DataPoint
import json
import logging

logger = logging.getLogger(__name__)

class FitbitAPI:
    """Fitbit Web API client"""
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.fitbit.com/1/user/-"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
    
    def test_connection(self):
        """Test if the access token is valid"""
        try:
            response = requests.get(f"{self.base_url}/profile.json", headers=self.headers)
            if response.status_code == 200:
                profile = response.json()
                return True, profile.get('user', {}).get('displayName', 'Unknown')
            elif response.status_code == 401:
                return False, "Invalid or expired access token"
            else:
                return False, f"API request failed: {response.status_code}"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def fetch_activity_data(self, start_date, end_date):
        """Fetch activity data (steps, calories, distance, etc.)"""
        try:
            # Get daily activity summary
            url = f"{self.base_url}/activities/date/{start_date}/{end_date}.json"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise Exception("Invalid or expired Fitbit access token")
            else:
                raise Exception(f"Fitbit API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error fetching Fitbit activity data: {e}")
            raise
    
    def fetch_heart_rate_data(self, start_date, end_date):
        """Fetch heart rate data"""
        try:
            # Get daily heart rate summary
            url = f"{self.base_url}/activities/heart/date/{start_date}/{end_date}.json"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise Exception("Invalid or expired Fitbit access token")
            else:
                raise Exception(f"Fitbit API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error fetching Fitbit heart rate data: {e}")
            raise
    
    def fetch_sleep_data(self, start_date, end_date):
        """Fetch sleep data"""
        try:
            # Get sleep data
            url = f"{self.base_url}/sleep/date/{start_date}/{end_date}.json"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise Exception("Invalid or expired Fitbit access token")
            else:
                raise Exception(f"Fitbit API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error fetching Fitbit sleep data: {e}")
            raise
    
    def fetch_body_data(self, start_date, end_date):
        """Fetch body composition data (weight, BMI, etc.)"""
        try:
            # Get body weight data
            url = f"{self.base_url}/body/log/weight/date/{start_date}/{end_date}.json"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise Exception("Invalid or expired Fitbit access token")
            else:
                raise Exception(f"Fitbit API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error fetching Fitbit body data: {e}")
            raise

def fetch_fitbit_data(access_token, start_date_str, end_date_str):
    """
    Fetch all Fitbit data for a date range
    
    Args:
        access_token: Fitbit OAuth access token
        start_date_str: Start date in YYYY-MM-DD format
        end_date_str: End date in YYYY-MM-DD format
    
    Returns:
        dict: Combined data from all Fitbit endpoints
    """
    try:
        print(f"🔍 Starting Fitbit data fetch from {start_date_str} to {end_date_str}")
        fitbit = FitbitAPI(access_token)
        
        # Test connection first
        is_valid, message = fitbit.test_connection()
        if not is_valid:
            print(f"❌ Fitbit connection failed: {message}")
            raise Exception(f"Fitbit connection failed: {message}")
        
        print(f"✅ Successfully connected to Fitbit for user: {message}")
        logger.info(f"Successfully connected to Fitbit for user: {message}")
        
        # Fetch data from all endpoints
        all_data = {
            'activity': [],
            'heart_rate': [],
            'sleep': [],
            'body': []
        }
        
        # Process each day in the range
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            try:
                print(f"📅 Fetching data for {date_str}")
                
                # Fetch activity data
                activity_data = fitbit.fetch_activity_data(date_str, date_str)
                if activity_data:
                    print(f"✅ Activity data for {date_str}: {json.dumps(activity_data, indent=2)[:200]}...")
                    all_data['activity'].append({
                        'date': date_str,
                        'data': activity_data
                    })
                else:
                    print(f"⚠️ No activity data for {date_str}")
                
                # Fetch heart rate data
                hr_data = fitbit.fetch_heart_rate_data(date_str, date_str)
                if hr_data:
                    print(f"✅ Heart rate data for {date_str}: {json.dumps(hr_data, indent=2)[:200]}...")
                    all_data['heart_rate'].append({
                        'date': date_str,
                        'data': hr_data
                    })
                else:
                    print(f"⚠️ No heart rate data for {date_str}")
                
                # Fetch sleep data
                sleep_data = fitbit.fetch_sleep_data(date_str, date_str)
                if sleep_data:
                    print(f"✅ Sleep data for {date_str}: {json.dumps(sleep_data, indent=2)[:200]}...")
                    all_data['sleep'].append({
                        'date': date_str,
                        'data': sleep_data
                    })
                else:
                    print(f"⚠️ No sleep data for {date_str}")
                
                # Fetch body data
                body_data = fitbit.fetch_body_data(date_str, date_str)
                if body_data:
                    print(f"✅ Body data for {date_str}: {json.dumps(body_data, indent=2)[:200]}...")
                    all_data['body'].append({
                        'date': date_str,
                        'data': body_data
                    })
                else:
                    print(f"⚠️ No body data for {date_str}")
                
            except Exception as e:
                print(f"❌ Failed to fetch data for {date_str}: {e}")
                logger.warning(f"Failed to fetch data for {date_str}: {e}")
                # Continue with other dates even if one fails
            
            current_date += timedelta(days=1)
        
        return all_data
        
    except Exception as e:
        logger.error(f"Error fetching Fitbit data: {e}")
        raise

def clean_fitbit_data(raw_data):
    """
    Clean and normalize Fitbit data for storage
    
    Args:
        raw_data: Raw data from Fitbit API
    
    Returns:
        list: Cleaned data points ready for database storage
    """
    cleaned_records = []
    
    try:
        # Process activity data
        for activity_entry in raw_data.get('activity', []):
            date_str = activity_entry['date']
            activity_data = activity_entry['data']
            
            # Extract activity summary data
            if 'summary' in activity_data:
                summary = activity_data['summary']
                
                # Map Fitbit fields to our metric names
                activity_mappings = {
                    'steps': 'fitbit_steps',
                    'caloriesOut': 'fitbit_calories_burned',
                    'distances': 'fitbit_distance',  # This is an array, we'll take the first one
                    'activeMinutes': 'fitbit_active_minutes',
                    'floors': 'fitbit_floors',
                    'elevation': 'fitbit_elevation'
                }
                
                for fitbit_field, our_metric in activity_mappings.items():
                    if fitbit_field in summary and summary[fitbit_field] is not None:
                        value = summary[fitbit_field]
                        
                        # Handle special cases
                        if fitbit_field == 'distances' and isinstance(value, list) and len(value) > 0:
                            value = value[0].get('distance', 0)
                        
                        cleaned_records.append({
                            'date': date_str,
                            'metric_name': our_metric,
                            'value': float(value)
                        })
        
        # Process heart rate data
        for hr_entry in raw_data.get('heart_rate', []):
            date_str = hr_entry['date']
            hr_data = hr_entry['data']
            
            if 'activities-heart' in hr_data and len(hr_data['activities-heart']) > 0:
                heart_data = hr_data['activities-heart'][0]
                
                # Resting heart rate
                if 'value' in heart_data and 'restingHeartRate' in heart_data['value']:
                    cleaned_records.append({
                        'date': date_str,
                        'metric_name': 'fitbit_resting_heart_rate',
                        'value': float(heart_data['value']['restingHeartRate'])
                    })
                
                # Heart rate zones (if available)
                if 'value' in heart_data and 'heartRateZones' in heart_data['value']:
                    zones = heart_data['value']['heartRateZones']
                    for zone in zones:
                        if 'minutes' in zone and zone['minutes'] > 0:
                            zone_name = zone.get('name', 'unknown').lower().replace(' ', '_')
                            cleaned_records.append({
                                'date': date_str,
                                'metric_name': f'fitbit_hr_zone_{zone_name}_minutes',
                                'value': float(zone['minutes'])
                            })
        
        # Process sleep data
        for sleep_entry in raw_data.get('sleep', []):
            date_str = sleep_entry['date']
            sleep_data = sleep_entry['data']
            
            if 'sleep' in sleep_data and len(sleep_data['sleep']) > 0:
                sleep_summary = sleep_data['sleep'][0]
                
                # Map sleep metrics
                sleep_mappings = {
                    'minutesAsleep': 'fitbit_sleep_duration',
                    'minutesAwake': 'fitbit_awake_time',
                    'efficiency': 'fitbit_sleep_efficiency',
                    'timeInBed': 'fitbit_time_in_bed',
                    'minutesToFallAsleep': 'fitbit_sleep_latency'
                }
                
                for fitbit_field, our_metric in sleep_mappings.items():
                    if fitbit_field in sleep_summary and sleep_summary[fitbit_field] is not None:
                        cleaned_records.append({
                            'date': date_str,
                            'metric_name': our_metric,
                            'value': float(sleep_summary[fitbit_field])
                        })
                
                # Process sleep stages if available
                if 'levels' in sleep_summary and 'summary' in sleep_summary['levels']:
                    stages = sleep_summary['levels']['summary']
                    stage_mappings = {
                        'deep': 'fitbit_deep_sleep_minutes',
                        'light': 'fitbit_light_sleep_minutes',
                        'rem': 'fitbit_rem_sleep_minutes',
                        'wake': 'fitbit_wake_minutes'
                    }
                    
                    for fitbit_stage, our_metric in stage_mappings.items():
                        if fitbit_stage in stages and stages[fitbit_stage] is not None:
                            cleaned_records.append({
                                'date': date_str,
                                'metric_name': our_metric,
                                'value': float(stages[fitbit_stage])
                            })
        
        # Process body data
        for body_entry in raw_data.get('body', []):
            date_str = body_entry['date']
            body_data = body_entry['data']
            
            if 'weight' in body_data and len(body_data['weight']) > 0:
                weight_data = body_data['weight'][0]
                
                if 'weight' in weight_data:
                    cleaned_records.append({
                        'date': date_str,
                        'metric_name': 'fitbit_weight',
                        'value': float(weight_data['weight'])
                    })
                
                if 'bmi' in weight_data:
                    cleaned_records.append({
                        'date': date_str,
                        'metric_name': 'fitbit_bmi',
                        'value': float(weight_data['bmi'])
                    })
        
        print(f"✅ Cleaned {len(cleaned_records)} Fitbit data points")
        logger.info(f"Cleaned {len(cleaned_records)} Fitbit data points")
        
        # Log sample of cleaned records
        if cleaned_records:
            print("📊 Sample cleaned records:")
            for i, record in enumerate(cleaned_records[:5]):  # Show first 5
                print(f"  {i+1}. {record['date']} - {record['metric_name']}: {record['value']}")
        
        return cleaned_records
        
    except Exception as e:
        logger.error(f"Error cleaning Fitbit data: {e}")
        raise

def store_fitbit_data(cleaned_records):
    """
    Store cleaned Fitbit data in the database
    
    Args:
        cleaned_records: List of cleaned data records
    
    Returns:
        int: Number of records inserted
    """
    try:
        # Get or create Fitbit graph
        fitbit_graph = Graph.query.filter_by(name="Fitbit Data").first()
        if not fitbit_graph:
            fitbit_graph = Graph(
                name="Fitbit Data", 
                description="Data from Fitbit Web API",
                is_temporary=False
            )
            db.session.add(fitbit_graph)
            db.session.commit()
        
        new_data_points = []
        
        for record in cleaned_records:
            date_str = record.get("date")
            if not date_str:
                continue
            
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            metric_name = record.get("metric_name")
            value = record.get("value")
            
            if not all([date_obj, metric_name, value is not None]):
                continue
            
            # Check if data point already exists
            existing_dp = DataPoint.query.filter_by(
                date=date_obj,
                metric_name=metric_name,
                graph_id=fitbit_graph.id
            ).first()
            
            if not existing_dp:
                new_data_points.append(
                    DataPoint(
                        date=date_obj,
                        metric_name=metric_name,
                        value=float(value),
                        graph_id=fitbit_graph.id
                    )
                )
        
        # Bulk insert new data points
        if new_data_points:
            print(f"💾 Storing {len(new_data_points)} new Fitbit data points...")
            db.session.bulk_save_objects(new_data_points)
            db.session.commit()
            print(f"✅ Successfully stored {len(new_data_points)} new Fitbit data points")
            logger.info(f"Stored {len(new_data_points)} new Fitbit data points")
        else:
            print("ℹ️ No new data points to store (all data already exists)")
        
        return len(new_data_points)
        
    except Exception as e:
        logger.error(f"Error storing Fitbit data: {e}")
        db.session.rollback()
        raise

# Test function
if __name__ == '__main__':
    # This would be used for testing with a real access token
    print("Fitbit integration module loaded successfully")
