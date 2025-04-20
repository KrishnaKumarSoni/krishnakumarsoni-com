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

def get_formatted_private_key():
    """Get and format the private key from environment variables"""
    try:
        # Get raw key from environment
        key = os.getenv('AUTH_PRIVATE_KEY', '')
        if not key:
            print("No private key found in environment variables")
            return None
            
        # Strip any wrapping quotes and whitespace
        key = key.strip().strip('"\'')
        
        # Check for header/footer
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        
        if header not in key or footer not in key:
            print("Private key missing header or footer")
            return None
            
        # Split the key into parts and clean
        parts = key.split('\\n')
        parts = [part.strip() for part in parts if part.strip()]
        
        # Ensure header and footer are separate lines
        if parts[0] != header:
            parts[0] = header
        if parts[-1] != footer:
            parts[-1] = footer
            
        # Join with actual newlines and ensure final newline
        formatted_key = '\n'.join(parts) + '\n'
            
        # Debug output
        print(f"Formatted key has {len(parts)} lines")
        print(f"Header present: {formatted_key.startswith(header)}")
        print(f"Footer present: {formatted_key.endswith(footer + '\n')}")
        
        return formatted_key
        
    except Exception as e:
        print(f"Error formatting private key: {str(e)}")
        return None

def get_database_credentials():
    """Get credentials for database Firebase project"""
    private_key = get_formatted_private_key()
    if not private_key:
        return None
        
    return {
        'type': 'service_account',
        'project_id': os.getenv('FIREBASE_PROJECT_ID'),
        'private_key': private_key,
        'client_email': os.getenv('AUTH_CLIENT_EMAIL'),
        'auth_uri': "https://accounts.google.com/o/oauth2/auth",
        'token_uri': "https://oauth2.googleapis.com/token",
        'auth_provider_x509_cert_url': "https://www.googleapis.com/oauth2/v1/certs",
        'client_x509_cert_url': os.getenv('AUTH_CLIENT_CERT_URL')
    }

def validate_database_credentials(creds):
    """Validate the minimal required credentials for database"""
    required = [
        'type', 
        'project_id', 
        'private_key', 
        'client_email',
        'token_uri'  # Required by Firebase Admin SDK
    ]
    
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
        if not creds:
            print("Failed to get database credentials")
            return None
            
        # Debug output
        print("\nDatabase Firebase Credentials Status:")
        print(f"Project ID: {creds.get('project_id')}")
        print(f"Client Email: {creds.get('client_email')}")
        print(f"Private Key present: {bool(creds.get('private_key'))}")
        print(f"Token URI present: {bool(creds.get('token_uri'))}")
        
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
__all__ = ['db', 'storage_bucket', 'get_formatted_private_key'] 