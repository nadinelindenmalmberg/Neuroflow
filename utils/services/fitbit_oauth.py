"""
Fitbit OAuth 2.0 Integration
Handles the OAuth flow for Fitbit Web API authorization
"""
import requests
import base64
import urllib.parse
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FitbitOAuth:
    """Handles Fitbit OAuth 2.0 authorization flow"""
    
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://www.fitbit.com/oauth2/authorize"
        self.token_url = "https://api.fitbit.com/oauth2/token"
        
    def get_authorization_url(self, state=None):
        """
        Generate the authorization URL for user to visit
        
        Args:
            state: Optional state parameter for security
            
        Returns:
            str: Authorization URL
        """
        # Required scopes for health data access
        scopes = [
            'activity',      # Activity data (steps, calories, etc.)
            'heartrate',     # Heart rate data
            'sleep',         # Sleep data
            'weight',        # Weight and body composition
            'profile'        # Basic profile information
        ]
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes),
            'expires_in': '604800'  # 7 days
        }
        
        if state:
            params['state'] = state
            
        auth_url = f"{self.auth_url}?{urllib.parse.urlencode(params)}"
        return auth_url
    
    def exchange_code_for_tokens(self, authorization_code):
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            authorization_code: Code received from Fitbit after user authorization
            
        Returns:
            dict: Token response with access_token, refresh_token, etc.
        """
        try:
            # Prepare the request
            headers = {
                'Authorization': f'Basic {self._get_basic_auth_header()}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(self.token_url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                logger.info("Successfully obtained Fitbit tokens")
                return {
                    'success': True,
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token'),
                    'expires_in': token_data.get('expires_in'),
                    'scope': token_data.get('scope'),
                    'token_type': token_data.get('token_type'),
                    'user_id': token_data.get('user_id')
                }
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('errors', [{}])[0].get('message', 'Unknown error')
                logger.error(f"Failed to exchange code for tokens: {response.status_code} - {error_msg}")
                return {
                    'success': False,
                    'error': f"Token exchange failed: {error_msg}",
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            return {
                'success': False,
                'error': f"Token exchange error: {str(e)}"
            }
    
    def refresh_access_token(self, refresh_token):
        """
        Refresh an expired access token using the refresh token
        
        Args:
            refresh_token: The refresh token from initial authorization
            
        Returns:
            dict: New token response
        """
        try:
            headers = {
                'Authorization': f'Basic {self._get_basic_auth_header()}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            response = requests.post(self.token_url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                logger.info("Successfully refreshed Fitbit access token")
                return {
                    'success': True,
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token', refresh_token),  # Keep old if not provided
                    'expires_in': token_data.get('expires_in'),
                    'scope': token_data.get('scope'),
                    'token_type': token_data.get('token_type')
                }
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('errors', [{}])[0].get('message', 'Unknown error')
                logger.error(f"Failed to refresh token: {response.status_code} - {error_msg}")
                return {
                    'success': False,
                    'error': f"Token refresh failed: {error_msg}",
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return {
                'success': False,
                'error': f"Token refresh error: {str(e)}"
            }
    
    def _get_basic_auth_header(self):
        """Generate Basic Auth header for Fitbit API"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return encoded_credentials
    
    def revoke_token(self, access_token):
        """
        Revoke an access token (logout)
        
        Args:
            access_token: The access token to revoke
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'token': access_token
            }
            
            response = requests.post(
                'https://api.fitbit.com/oauth2/revoke',
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                logger.info("Successfully revoked Fitbit token")
                return True
            else:
                logger.error(f"Failed to revoke token: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

# Helper function to get Fitbit OAuth instance
def get_fitbit_oauth():
    """
    Get configured Fitbit OAuth instance
    
    Returns:
        FitbitOAuth: Configured OAuth instance
    """
    import os
    
    client_id = os.getenv('FITBIT_CLIENT_ID')
    client_secret = os.getenv('FITBIT_CLIENT_SECRET')
    redirect_uri = os.getenv('FITBIT_REDIRECT_URI', 'http://localhost:5174/auth/fitbit/callback')
    
    if not client_id or not client_secret:
        raise ValueError("FITBIT_CLIENT_ID and FITBIT_CLIENT_SECRET must be set in environment variables")
    
    return FitbitOAuth(client_id, client_secret, redirect_uri)

