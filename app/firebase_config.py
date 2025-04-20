import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth

# Load environment variables
load_dotenv()

# Debug: Print environment variables
print("Environment variables loaded")

# Singleton pattern for Firebase apps
_db_firebase_app = None
_db = None
_storage_bucket = None

def get_database_credentials():
    """Get credentials for database Firebase project"""
    return {
        'type': 'service_account',
        'project_id': os.getenv('FIREBASE_PROJECT_ID'),
        'private_key': os.getenv('AUTH_PRIVATE_KEY'),  # Reusing auth key for now
        'client_email': os.getenv('AUTH_CLIENT_EMAIL'),  # Reusing auth email for now
    }

def validate_database_credentials(creds):
    """Validate the minimal required credentials for database"""
    required = ['type', 'project_id', 'private_key', 'client_email']
    
    # Check required fields
    missing = [field for field in required if not creds.get(field)]
    if missing:
        print(f"Missing required database fields: {', '.join(missing)}")
        return False
        
    return True

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
            
        # Get database credentials
        creds = get_database_credentials()
        
        # Debug output
        print("\nDatabase Firebase Credentials Status:")
        print(f"Project ID: {creds.get('project_id')}")
        print(f"Client Email: {creds.get('client_email')}")
        print(f"Private Key present: {bool(creds.get('private_key'))}")
        
        # Validate credentials
        if not validate_database_credentials(creds):
            print("Invalid database credentials")
            return None
            
        # Initialize Firebase app for database
        cert = credentials.Certificate(creds)
        _db_firebase_app = firebase_admin.initialize_app(cert, name='database')
        
        # Initialize services
        _db = firestore.client(app=_db_firebase_app)
        _storage_bucket = storage.bucket(app=_db_firebase_app)
        
        print("Database Firebase initialized successfully")
        return _db_firebase_app, _db, _storage_bucket
        
    except Exception as e:
        print(f"Error initializing database Firebase: {str(e)}")
        return None

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
__all__ = ['db', 'storage_bucket'] 