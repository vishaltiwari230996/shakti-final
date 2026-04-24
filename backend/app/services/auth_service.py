"""
Google OAuth Authentication Service
Handles user authentication, token verification, and usage tracking
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# In-memory user database (replace with real DB for production)
USERS_DB = {}
USAGE_DB = {}

class AuthService:
    """Google OAuth authentication and token management"""
    
    DEFAULT_GOOGLE_CLIENT_ID = "507981386398-q7q45uuob1urd87egacnojdja9j9puc1.apps.googleusercontent.com"

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or DEFAULT_GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    @staticmethod
    def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Google ID token and extract user information
        
        Args:
            token: ID token from Google OAuth
            
        Returns:
            User data dict or None if invalid
        """
        try:
            # Verify the token with Google (allow 60s clock skew tolerance)
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(),
                AuthService.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=60
            )
            
            # Token is valid
            return {
                'user_id': idinfo.get('sub'),
                'email': idinfo.get('email'),
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture'),
                'email_verified': idinfo.get('email_verified'),
            }
        except ValueError as e:
            print(f"❌ Invalid token: {e}")
            return None
        except Exception as e:
            print(f"❌ Token verification error: {e}")
            return None
    
    @staticmethod
    def create_or_update_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update user in database
        
        Args:
            user_data: User info from Google token
            
        Returns:
            User record with usage info
        """
        user_id = user_data.get('user_id')
        
        if user_id not in USERS_DB:
            # New user
            USERS_DB[user_id] = {
                'user_id': user_id,
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'picture': user_data.get('picture'),
                'created_at': datetime.utcnow().isoformat(),
                'last_login': datetime.utcnow().isoformat(),
            }
            
            # Initialize usage limits
            USAGE_DB[user_id] = {
                'user_id': user_id,
                'product_analysis_count': 0,
                'product_analysis_reset': (datetime.utcnow() + timedelta(hours=72)).isoformat(),
                'batch_optimize_count': 0,
                'batch_optimize_reset': (datetime.utcnow() + timedelta(hours=72)).isoformat(),
            }
            
            print(f"✅ New user created: {user_data.get('email')}")
        else:
            # Update last login
            USERS_DB[user_id]['last_login'] = datetime.utcnow().isoformat()
            print(f"✅ User logged in: {user_data.get('email')}")
        
        return USERS_DB[user_id]
    
    @staticmethod
    def check_usage_limit(user_id: str, operation: str) -> Dict[str, Any]:
        """
        Check if user has remaining quota for operation
        
        Args:
            user_id: User ID from Google token
            operation: 'product_analysis' or 'batch_optimize'
            
        Returns:
            Dict with 'allowed' bool and 'remaining' count
        """
        if user_id not in USAGE_DB:
            return {'allowed': False, 'remaining': 0, 'error': 'User not found'}
        
        usage = USAGE_DB[user_id]
        now = datetime.utcnow()
        
        if operation == 'product_analysis':
            count_key = 'product_analysis_count'
            reset_key = 'product_analysis_reset'
            limit = 10
        elif operation == 'batch_optimize':
            count_key = 'batch_optimize_count'
            reset_key = 'batch_optimize_reset'
            limit = 10
        else:
            return {'allowed': False, 'remaining': 0, 'error': 'Invalid operation'}
        
        # Check if reset window has passed
        reset_time = datetime.fromisoformat(usage[reset_key])
        if now > reset_time:
            # Reset the counter
            usage[count_key] = 0
            usage[reset_key] = (now + timedelta(hours=72)).isoformat()
        
        current_count = usage[count_key]
        remaining = limit - current_count
        allowed = remaining > 0
        
        return {
            'allowed': allowed,
            'remaining': remaining,
            'used': current_count,
            'limit': limit,
            'resets_at': usage[reset_key]
        }
    
    @staticmethod
    def increment_usage(user_id: str, operation: str) -> Dict[str, Any]:
        """
        Increment usage counter for operation
        
        Args:
            user_id: User ID from Google token
            operation: 'product_analysis' or 'batch_optimize'
            
        Returns:
            Updated usage info
        """
        if user_id not in USAGE_DB:
            return {'success': False, 'error': 'User not found'}
        
        usage = USAGE_DB[user_id]
        
        if operation == 'product_analysis':
            count_key = 'product_analysis_count'
        elif operation == 'batch_optimize':
            count_key = 'batch_optimize_count'
        else:
            return {'success': False, 'error': 'Invalid operation'}
        
        usage[count_key] += 1
        
        return {
            'success': True,
            'count': usage[count_key]
        }
    
    @staticmethod
    def get_user_stats(user_id: str) -> Dict[str, Any]:
        """
        Get user's current usage statistics
        
        Args:
            user_id: User ID from Google token
            
        Returns:
            User stats including usage limits
        """
        if user_id not in USERS_DB or user_id not in USAGE_DB:
            return None
        
        user = USERS_DB[user_id]
        usage = USAGE_DB[user_id]
        
        now = datetime.utcnow()
        
        # Check if reset windows have passed
        pa_reset = datetime.fromisoformat(usage['product_analysis_reset'])
        if now > pa_reset:
            usage['product_analysis_count'] = 0
            usage['product_analysis_reset'] = (now + timedelta(hours=72)).isoformat()
        
        bo_reset = datetime.fromisoformat(usage['batch_optimize_reset'])
        if now > bo_reset:
            usage['batch_optimize_count'] = 0
            usage['batch_optimize_reset'] = (now + timedelta(hours=72)).isoformat()
        
        return {
            'user': user,
            'usage': {
                'product_analysis': {
                    'used': usage['product_analysis_count'],
                    'limit': 10,
                    'remaining': 10 - usage['product_analysis_count'],
                    'resets_at': usage['product_analysis_reset']
                },
                'batch_optimize': {
                    'used': usage['batch_optimize_count'],
                    'limit': 10,
                    'remaining': 10 - usage['batch_optimize_count'],
                    'resets_at': usage['batch_optimize_reset']
                }
            }
        }
