import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage
import base64

# Load environment variables
load_dotenv()

# Debug: Print environment variables
print("Environment variables loaded")

# Singleton pattern for Firebase apps
_db_firebase_app = None
_auth_firebase_app = None
_db = None
_storage_bucket = None

def get_formatted_private_key():
    """Format the private key from environment variable."""
    try:
        private_key = os.getenv('AUTH_PRIVATE_KEY', '')
        if not private_key:
            print("Error: AUTH_PRIVATE_KEY not found in environment variables")
            return None

        # Remove quotes and whitespace
        private_key = private_key.strip().strip('"\'')
        
        # Check if key already has proper format
        if private_key.startswith('-----BEGIN PRIVATE KEY-----') and private_key.endswith('-----END PRIVATE KEY-----'):
            # Split the key into lines if it's not already
            if '\n' not in private_key:
                parts = private_key.split('-----')
                base64_str = parts[2].strip()
                formatted_key = (
                    '-----BEGIN PRIVATE KEY-----\n' +
                    '\n'.join(base64_str[i:i+64] for i in range(0, len(base64_str), 64)) +
                    '\n-----END PRIVATE KEY-----\n'
                )
                return formatted_key
            return private_key

        # If key is just base64 content
        if '\n' not in private_key:
            formatted_key = (
                '-----BEGIN PRIVATE KEY-----\n' +
                '\n'.join(private_key[i:i+64] for i in range(0, len(private_key), 64)) +
                '\n-----END PRIVATE KEY-----\n'
            )
            return formatted_key

        return private_key
    except Exception as e:
        print(f"Error formatting private key: {str(e)}")
        return None

def initialize_firebase_auth():
    """Initialize Firebase for authentication operations"""
    global _auth_firebase_app
    
    try:
        # Check if already initialized
        try:
            _auth_firebase_app = firebase_admin.get_app('auth')
            return _auth_firebase_app
        except ValueError:
            pass  # App not initialized yet
            
        # Get auth service account info
        private_key = get_formatted_private_key()
        if not private_key:
            raise ValueError("Could not format private key")
            
        cred = credentials.Certificate({
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
        })
        
        # Initialize Firebase app for auth
        _auth_firebase_app = firebase_admin.initialize_app(
            cred,
            name='auth'
        )
        
        print("Auth Firebase initialized successfully")
        return _auth_firebase_app
        
    except Exception as e:
        print(f"Error initializing auth Firebase: {str(e)}")
        return None

def initialize_firebase_database():
    """Initialize Firebase for database operations"""
    global _db_firebase_app, _db, _storage_bucket
    
    try:
        # Check if already initialized
        try:
            _db_firebase_app = firebase_admin.get_app('database')
            return _db_firebase_app, _db, _storage_bucket
        except ValueError:
            pass  # App not initialized yet
            
        # Get database config
        config = {
            'apiKey': os.getenv('FIREBASE_API_KEY'),
            'projectId': os.getenv('FIREBASE_PROJECT_ID'),
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
            'appId': os.getenv('FIREBASE_APP_ID'),
            'measurementId': os.getenv('FIREBASE_MEASUREMENT_ID')
        }
        
        # Debug output
        print("\nDatabase Firebase Config Status:")
        for key, value in config.items():
            print(f"{key}: {'Present' if value else 'Missing'}")
        
        # Initialize Firebase app for database
        _db_firebase_app = firebase_admin.initialize_app(
            None,  # Use default credentials
            {
                'projectId': config['projectId'],
                'storageBucket': config['storageBucket']
            },
            name='database'
        )
        
        # Initialize services
        _db = firestore.client(app=_db_firebase_app)
        _storage_bucket = storage.bucket(app=_db_firebase_app)
        
        print("Database Firebase initialized successfully")
        return _db_firebase_app, _db, _storage_bucket
        
    except Exception as e:
        print(f"Error initializing database Firebase: {str(e)}")
        return None

# Initialize Firebase auth
try:
    auth_app = initialize_firebase_auth()
    if not auth_app:
        print("Warning: Auth Firebase initialization failed")
except Exception as e:
    print(f"Error in auth initialization: {str(e)}")

# Initialize Firebase database
try:
    result = initialize_firebase_database()
    if result:
        app, db, storage_bucket = result
    else:
        print("Warning: Database Firebase initialization failed")
        db = None
        storage_bucket = None
except Exception as e:
    print(f"Error in database initialization: {str(e)}")
    db = None
    storage_bucket = None

# Export for use in other modules
__all__ = ['db', 'storage_bucket', 'get_formatted_private_key']