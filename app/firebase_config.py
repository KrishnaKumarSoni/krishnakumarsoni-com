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
    """Format the private key correctly for both Vercel and local environments"""
    key = os.getenv('AUTH_PRIVATE_KEY')
    if not key:
        print("No private key found in environment variables")
        return None
        
    # Remove any quotes and whitespace
    key = key.strip().strip('"').strip("'")
    
    # Ensure the key has the correct header and footer
    if not key.startswith('-----BEGIN PRIVATE KEY-----'):
        print("Private key is missing proper header")
        return None
    if not key.endswith('-----END PRIVATE KEY-----'):
        print("Private key is missing proper footer")
        return None
    
    # Replace literal \n with actual newlines if they exist
    if '\\n' in key:
        key = key.replace('\\n', '\n')
        
    # Ensure there's a newline after the header and before the footer
    key = key.replace('-----BEGIN PRIVATE KEY-----', '-----BEGIN PRIVATE KEY-----\n')
    key = key.replace('-----END PRIVATE KEY-----', '\n-----END PRIVATE KEY-----')
    
    # Ensure the key content is on separate lines
    parts = key.split('\n')
    cleaned_parts = []
    for part in parts:
        if part and not part.startswith('-----') and not part.endswith('-----'):
            # Clean up any remaining whitespace in key content
            cleaned_parts.append(part.strip())
        else:
            cleaned_parts.append(part)
            
    # Rejoin with proper newlines
    key = '\n'.join(p for p in cleaned_parts if p)
    
    # Ensure final newline
    if not key.endswith('\n'):
        key += '\n'
        
    return key

def validate_service_account_info(info):
    """Validate the service account info before using it"""
    required_fields = [
        'project_id',
        'private_key',
        'client_email',
        'client_id',
        'private_key_id',
        'type'  # Ensure type field is present
    ]
    
    missing = [field for field in required_fields if not info.get(field)]
    if missing:
        print(f"Missing required fields: {', '.join(missing)}")
        return False
        
    # Validate private key format
    private_key = info.get('private_key', '')
    if not private_key:
        print("Private key is missing")
        return False
        
    if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
        print("Private key missing proper header")
        return False
        
    if not private_key.endswith('-----END PRIVATE KEY-----\n'):
        print("Private key missing proper footer")
        return False
        
    # Validate type
    if info.get('type') != 'service_account':
        print("Invalid credential type - must be 'service_account'")
        return False
        
    return True

def initialize_firebase():
    """Initialize Firebase Admin SDK with environment variables for Vercel compatibility"""
    global _firebase_app, _db, _storage_bucket
    
    if _firebase_app:
        return _db, _storage_bucket
    
    try:
        # Format the private key correctly for Vercel
        private_key = get_formatted_private_key()
        if not private_key:
            raise ValueError("Could not format private key")
            
        print("Private key format check:")
        print(f"Starts with header: {private_key.startswith('-----BEGIN PRIVATE KEY-----')}")
        print(f"Ends with footer: {private_key.endswith('-----END PRIVATE KEY-----\n')}")
        print(f"Contains newlines: {'\\n' in private_key}")
        
        # Create service account info directly from environment variables
        service_account_info = {
            "type": "service_account",
            "project_id": os.getenv('AUTH_PROJECT_ID'),
            "private_key_id": os.getenv('AUTH_PRIVATE_KEY_ID'),
            "private_key": private_key,
            "client_email": os.getenv('AUTH_CLIENT_EMAIL'),
            "client_id": os.getenv('AUTH_CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv('AUTH_CLIENT_CERT_URL')
        }
        
        # Validate service account info
        if not validate_service_account_info(service_account_info):
            raise ValueError("Invalid service account configuration")
            
        # Debug info (safely)
        print(f"Project ID: {service_account_info['project_id']}")
        print(f"Client Email: {service_account_info['client_email']}")
        
        # Initialize Firebase with dictionary credentials (works on Vercel)
        _firebase_app = firebase_admin.initialize_app(
            credentials.Certificate(service_account_info),
            {
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
                'projectId': os.getenv('FIREBASE_PROJECT_ID')
            }
        )
        
        # Initialize Firestore and Storage
        _db = firestore.client()
        _storage_bucket = storage.bucket()
        print("Firebase initialized successfully with environment variables!")
        return _db, _storage_bucket
        
    except Exception as e:
        print(f"Firebase initialization error: {str(e)}")
        print("Attempting to use default application credentials...")
        try:
            # Try using default credentials as fallback
            _firebase_app = firebase_admin.initialize_app()
            _db = firestore.client()
            _storage_bucket = storage.bucket()
            print("Firebase initialized with default credentials!")
            return _db, _storage_bucket
        except Exception as fallback_error:
            print(f"Fallback initialization failed: {str(fallback_error)}")
            return None, None

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