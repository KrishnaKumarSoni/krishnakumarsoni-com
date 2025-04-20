import re
import firebase_admin
from firebase_admin import auth, credentials
from flask import session
from typing import Dict, Any, Optional
import os
import requests
import time
import random
import string
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime, timedelta
from ..firebase_config import get_formatted_private_key  # Import our key formatting function

# Load environment variables from .env file
load_dotenv()

# Get environment variables
AUTH_API_KEY = os.getenv('AUTH_API_KEY')
AUTH_PROJECT_ID = os.getenv('AUTH_PROJECT_ID')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Validate required environment variables
if not AUTH_API_KEY or not AUTH_PROJECT_ID:
    raise ValueError("AUTH_API_KEY and AUTH_PROJECT_ID environment variables must be set")

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    raise ValueError("Twilio credentials must be set in environment variables")

# Initialize Firebase Admin with auth-specific credentials
def initialize_firebase_auth():
    """Initialize Firebase Admin SDK for authentication"""
    try:
        # Try to get existing app first
        return firebase_admin.get_app('auth')
    except ValueError:
        # App doesn't exist, create new one
        try:
            # Get formatted private key
            private_key = get_formatted_private_key()
            if not private_key:
                raise ValueError("Failed to format private key")
                
            # Debug output for key format
            print("\nPrivate Key Format Check:")
            print(f"Key starts with correct header: {private_key.startswith('-----BEGIN PRIVATE KEY-----')}")
            print(f"Key ends with correct footer: {private_key.endswith('-----END PRIVATE KEY-----\n')}")
            print(f"Number of lines: {len(private_key.splitlines())}")

            # Create credentials dictionary
            cred_dict = {
                'type': 'service_account',
                'project_id': os.getenv('AUTH_PROJECT_ID'),
                'private_key_id': os.getenv('AUTH_PRIVATE_KEY_ID'),
                'private_key': private_key,
                'client_email': os.getenv('AUTH_CLIENT_EMAIL'),
                'client_id': os.getenv('AUTH_CLIENT_ID'),
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
                'client_x509_cert_url': os.getenv('AUTH_CLIENT_CERT_URL')
            }
            
            # Validate required fields
            required_fields = ['project_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if not cred_dict.get(field)]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            # Initialize app with credentials
            cred = credentials.Certificate(cred_dict)
            return firebase_admin.initialize_app(cred, name='auth')
            
        except Exception as e:
            print(f"\nFailed to initialize Firebase Auth: {str(e)}")
            print("\nEnvironment variables status:")
            for key in ['AUTH_PROJECT_ID', 'AUTH_PRIVATE_KEY_ID', 'AUTH_PRIVATE_KEY', 
                       'AUTH_CLIENT_EMAIL', 'AUTH_CLIENT_ID', 'AUTH_CLIENT_CERT_URL']:
                value = os.getenv(key)
                print(f"{key}: {'Present' if value else 'Missing'}")
            raise

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

FIREBASE_AUTH_BASE_URL = "https://identitytoolkit.googleapis.com/v1/accounts"

class PhoneAuthError(Exception):
    """Custom exception for phone authentication errors"""
    pass

def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number format"""
    pattern = r'^\+[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone_number))

def generate_verification_code() -> str:
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_sms(phone_number: str, code: str) -> bool:
    """Send verification code via Twilio SMS"""
    try:
        message = twilio_client.messages.create(
            body=f"Your verification code is: {code}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"SMS sending failed: {str(e)}")
        return False

def start_phone_verification(phone_number: str) -> Dict[str, Any]:
    """Start phone verification process"""
    if not validate_phone_number(phone_number):
        return {
            "success": False,
            "message": "Invalid phone number format. Must start with + and country code"
        }

    try:
        # Generate verification code
        code = generate_verification_code()
        
        # Store verification data in session
        session.permanent = True  # Enable permanent session
        session['phone_verification'] = {
            'phone_number': phone_number,
            'code': code,
            'attempts': 0,
            'expires_at': (datetime.now() + timedelta(minutes=5)).timestamp()
        }
        session.modified = True  # Mark session as modified
        
        # Send SMS via Twilio
        if send_verification_sms(phone_number, code):
            print(f"Verification code {code} sent to {phone_number}")  # For debugging
            return {
                "success": True,
                "message": "Verification code sent successfully"
            }
        else:
            session.pop('phone_verification', None)
            return {
                "success": False,
                "message": "Failed to send verification code"
            }

    except Exception as e:
        print(f"Error in start_phone_verification: {str(e)}")  # For debugging
        return {
            "success": False,
            "message": str(e)
        }

def verify_phone_otp(phone_number: str, code: str) -> Dict[str, Any]:
    """Verify phone OTP"""
    try:
        verification = session.get('phone_verification')
        print(f"Current session data: {verification}")  # For debugging
        
        if not verification:
            return {
                "success": False,
                "message": "No verification in progress"
            }

        # Check expiry
        if datetime.now().timestamp() > verification['expires_at']:
            session.pop('phone_verification', None)
            session.modified = True
            return {
                "success": False,
                "message": "Verification code expired"
            }

        # Check phone number match
        if phone_number != verification['phone_number']:
            return {
                "success": False,
                "message": "Phone number mismatch"
            }

        # Increment attempts
        verification['attempts'] += 1
        session['phone_verification'] = verification
        session.modified = True
        
        if verification['attempts'] > 3:
            session.pop('phone_verification', None)
            session.modified = True
            return {
                "success": False,
                "message": "Too many attempts. Please request a new code"
            }

        # Check code
        if code != verification['code']:
            print(f"Code mismatch. Expected {verification['code']}, got {code}")  # For debugging
            return {
                "success": False,
                "message": "Invalid verification code"
            }

        try:
            # Skip Firebase custom token creation if having issues
            # Instead, create a simple JWT token or use session-based auth
            
            # Store verified user info in session
            session.permanent = True
            session['user'] = {
                'phone_number': phone_number,
                'auth_time': int(time.time()),
                'is_verified': True
            }
            session.modified = True

            # Clean up verification data
            session.pop('phone_verification', None)
            
            print(f"Successfully verified {phone_number}")  # For debugging

            # Return success with session-based auth
            return {
                "success": True,
                "token": f"session-auth:{phone_number}:{int(time.time())}"
            }
        except Exception as token_error:
            print(f"Error creating auth token: {str(token_error)}")
            return {
                "success": False,
                "message": "Error creating authentication token"
            }

    except Exception as e:
        print(f"Error in verify_phone_otp: {str(e)}")  # For debugging
        return {
            "success": False,
            "message": "Verification failed"
        }

def check_auth() -> bool:
    """Check if user is authenticated"""
    user = session.get('user')
    if not user:
        return False
    
    # Check if authentication is valid (less than 24 hours old)
    if time.time() - user.get('auth_time', 0) > 86400:
        session.pop('user', None)
        return False
    
    # Check if user is verified
    if not user.get('is_verified'):
        return False
    
    return True

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated user"""
    return session.get('user')

def logout() -> Dict[str, Any]:
    """Logout user"""
    session.pop('user', None)
    return {"success": True}

def create_custom_token(uid: str) -> str:
    """Create a custom token for a user ID"""
    try:
        return auth.create_custom_token(uid).decode('utf-8')
    except Exception as e:
        print(f"Error creating custom token: {str(e)}")
        raise

def verify_id_token(id_token: str) -> Dict[str, Any]:
    """Verify Firebase ID token"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        raise

# Export the functions needed by routes
__all__ = [
    'start_phone_verification',
    'verify_phone_otp',
    'create_custom_token',
    'verify_id_token'
] 