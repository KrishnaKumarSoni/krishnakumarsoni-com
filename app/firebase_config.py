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
_firebase_app = None
_auth_firebase_app = None
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
            
        # Split the key into parts
        parts = key.split('\\n')
        
        # Remove empty parts and strip whitespace
        parts = [part.strip() for part in parts if part.strip()]
        
        # Ensure header and footer are separate lines
        if header in parts[0]:
            parts[0] = header
        if footer in parts[-1]:
            parts[-1] = footer
            
        # Join with actual newlines
        formatted_key = '\n'.join(parts)
        
        # Ensure final newline
        if not formatted_key.endswith('\n'):
            formatted_key += '\n'
            
        # Debug output
        print(f"Formatted key has {len(parts)} lines")
        print(f"Header present: {header in formatted_key}")
        print(f"Footer present: {footer in formatted_key}")
        print(f"Sample structure:\n{formatted_key[:100]}...")
        
        return formatted_key
        
    except Exception as e:
        print(f"Error formatting private key: {str(e)}")
        return None

def validate_service_account_info(info):
    """Validate service account credentials dictionary"""
    required_fields = ['type', 'project_id', 'private_key', 'client_email']
    
    # Check all required fields are present and non-empty
    for field in required_fields:
        if not info.get(field):
            print(f"Missing required field: {field}")
            return False
            
    # Validate private key format
    private_key = info['private_key']
    if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
        print("Private key missing header")
        return False
    if not private_key.endswith('-----END PRIVATE KEY-----\n'):
        print("Private key missing footer or final newline")
        return False
        
    # Count number of lines in private key
    key_lines = private_key.strip().split('\n')
    print(f"Private key has {len(key_lines)} lines")
    
    return True

def initialize_firebase():
    """Initialize Firebase with service account credentials"""
    try:
        # Check if already initialized
        try:
            return firebase_admin.get_app()
        except ValueError:
            pass  # App not initialized yet
            
        # Get and validate private key
        private_key = get_formatted_private_key()
        if not private_key:
            print("Failed to get formatted private key")
            return None
            
        # Get other required credentials
        project_id = os.getenv('AUTH_PROJECT_ID')
        client_email = os.getenv('AUTH_CLIENT_EMAIL')
        
        # Debug output for credentials
        print("\nFirebase Credentials Status:")
        print(f"Project ID present: {bool(project_id)}")
        print(f"Client email present: {bool(client_email)}")
        print(f"Private key present and formatted: {bool(private_key)}")
        
        # Create credentials dictionary
        creds = {
            'type': 'service_account',
            'project_id': project_id,
            'private_key': private_key,
            'client_email': client_email,
        }
        
        # Validate credentials
        if not validate_service_account_info(creds):
            print("Invalid service account credentials")
            return None
            
        # Initialize Firebase
        cred = credentials.Certificate(creds)
        app = firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully")
        return app
        
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
        print("\nEnvironment variables status:")
        for key in ['AUTH_PROJECT_ID', 'AUTH_CLIENT_EMAIL', 'AUTH_PRIVATE_KEY']:
            value = os.getenv(key)
            print(f"{key}: {'Present' if value else 'Missing'}")
        return None

# Try to initialize Firebase services
try:
    db, storage_bucket = initialize_firebase()
    if db is None:
        print("Warning: Firebase initialization failed, services will be unavailable")
except Exception as e:
    print(f"Error initializing Firebase. Application may not work properly: {str(e)}")
    # Set placeholder values to prevent import errors
    db = None
    storage_bucket = None

# Export for use in other modules
__all__ = ['db', 'storage_bucket', 'auth'] 