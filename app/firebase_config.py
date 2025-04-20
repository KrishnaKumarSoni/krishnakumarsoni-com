import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth

# Load environment variables
load_dotenv()

# Debug: Print environment variables
print("Environment variables loaded")

# Singleton pattern for Firebase
_firebase_app = None
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
        print(f"Sample structure:\n{formatted_key[:100]}...")
        
        return formatted_key
        
    except Exception as e:
        print(f"Error formatting private key: {str(e)}")
        return None

def validate_service_account_info(info, for_auth=False):
    """Validate service account credentials dictionary"""
    # Basic required fields for any Firebase service
    required_fields = ['type', 'project_id', 'private_key', 'client_email']
    
    # Additional fields required only for auth
    if for_auth:
        required_fields.extend([
            'private_key_id',
            'client_id',
            'auth_uri',
            'token_uri',
            'auth_provider_x509_cert_url',
            'client_x509_cert_url'
        ])
    
    # Check all required fields are present and non-empty
    missing = [field for field in required_fields if not info.get(field)]
    if missing:
        print(f"Missing required fields: {', '.join(missing)}")
        return False
            
    # Validate type
    if info['type'] != 'service_account':
        print("Invalid credential type - must be 'service_account'")
        return False
        
    # Validate private key format
    private_key = info.get('private_key', '')
    if not private_key:
        print("Private key is missing")
        return False
        
    # Split into lines and validate structure
    lines = private_key.strip().split('\n')
    if len(lines) < 3:
        print(f"Private key is malformed - found {len(lines)} lines, expected > 3")
        return False
            
    if not lines[0].strip() == "-----BEGIN PRIVATE KEY-----":
        print(f"Private key is missing proper header. Found: {lines[0]}")
        return False
            
    if not lines[-1].strip() == "-----END PRIVATE KEY-----":
        print(f"Private key is missing proper footer. Found: {lines[-1]}")
        return False
    
    return True

def initialize_firebase():
    """Initialize Firebase with service account credentials"""
    global db, storage_bucket
    
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
        
        # Create minimal credentials dictionary for database access
        creds = {
            'type': 'service_account',
            'project_id': project_id,
            'private_key': private_key,
            'client_email': client_email,
        }
        
        # Validate credentials (not for auth)
        if not validate_service_account_info(creds, for_auth=False):
            print("Invalid service account credentials")
            return None
            
        # Initialize Firebase
        cred = credentials.Certificate(creds)
        app = firebase_admin.initialize_app(cred)
        
        # Initialize Firestore and Storage
        db = firestore.client()
        storage_bucket = storage.bucket()
        
        print("Firebase initialized successfully with Firestore and Storage")
        return app, db, storage_bucket
        
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
        print("\nEnvironment variables status:")
        for key in ['AUTH_PROJECT_ID', 'AUTH_CLIENT_EMAIL', 'AUTH_PRIVATE_KEY']:
            value = os.getenv(key)
            print(f"{key}: {'Present' if value else 'Missing'}")
        return None

# Initialize Firebase services
try:
    result = initialize_firebase()
    if result:
        app, db, storage_bucket = result
    else:
        print("Warning: Firebase initialization failed, services will be unavailable")
        db = None
        storage_bucket = None
except Exception as e:
    print(f"Error initializing Firebase. Application may not work properly: {str(e)}")
    db = None
    storage_bucket = None

# Export for use in other modules
__all__ = ['db', 'storage_bucket', 'auth'] 