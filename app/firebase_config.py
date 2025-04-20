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
    """Format the private key correctly for both Vercel and local environments"""
    key = os.getenv('AUTH_PRIVATE_KEY')
    if not key:
        print("No private key found in environment variables")
        return None
        
    # Remove any quotes and whitespace
    key = key.strip().strip('"').strip("'")
    
    # Handle escaped newlines by first converting them to actual newlines
    key = key.replace('\\n', '\n')
    
    # Now split on actual newlines
    parts = key.split('\n')
    parts = [p for p in parts if p.strip()]  # Remove empty lines
    
    if len(parts) < 3:
        print("Private key appears malformed - not enough parts after splitting")
        print(f"Found {len(parts)} parts")
        print("Raw key length:", len(key))
        print("First few characters:", key[:50] + "...")
        return None
        
    # Reconstruct the key with proper line breaks
    formatted_parts = []
    for part in parts:
        part = part.strip()
        if part:  # Only add non-empty parts
            if part == "-----BEGIN PRIVATE KEY-----" or part == "-----END PRIVATE KEY-----":
                formatted_parts.append(part)
            else:
                # Add base64 content in chunks
                while part:
                    chunk = part[:64]
                    if chunk:  # Only add non-empty chunks
                        formatted_parts.append(chunk)
                    part = part[64:]
    
    # Join with proper newlines and ensure final newline
    formatted_key = '\n'.join(formatted_parts) + '\n'
    
    # Debug output
    print("\nKey formatting details:")
    print(f"1. Number of lines: {len(formatted_parts)}")
    print("2. Line lengths:")
    for i, line in enumerate(formatted_parts):
        if i < 3 or i > len(formatted_parts) - 3:  # Show first and last few lines
            print(f"   Line {i+1}: {len(line)} chars")
    print("3. Sample structure:")
    print(f"   First line: {formatted_parts[0]}")
    print(f"   Second line: {formatted_parts[1][:10]}...")
    print(f"   Last line: {formatted_parts[-1]}")
    print("4. Final newline present:", formatted_key.endswith('\n'))
    print("5. Raw key structure:")
    print(f"   Header present: {'-----BEGIN PRIVATE KEY-----' in formatted_key}")
    print(f"   Footer present: {'-----END PRIVATE KEY-----' in formatted_key}")
    print(f"   Number of line breaks: {formatted_key.count('\n')}")
    print(f"   Total key length: {len(formatted_key)}")
    
    return formatted_key

def validate_service_account_info(info):
    """Validate the service account info before using it"""
    required_fields = [
        'type',
        'project_id',
        'private_key_id',
        'private_key',
        'client_email',
        'client_id',
        'auth_uri',
        'token_uri',
        'auth_provider_x509_cert_url',
        'client_x509_cert_url'
    ]
    
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
    
    # Validate key structure
    if not (private_key.startswith('-----BEGIN PRIVATE KEY-----\n') and 
            private_key.endswith('\n-----END PRIVATE KEY-----\n')):
        print("Private key is missing proper header/footer structure")
        return False
    
    # Count number of lines and validate format
    lines = private_key.strip().split('\n')
    if len(lines) < 3:
        print(f"Private key is malformed - found {len(lines)} lines, expected > 3")
        return False
    
    # Validate base64 content
    content_lines = lines[1:-1]
    if not all(len(line.strip()) <= 64 for line in content_lines):
        print("Warning: Some content lines exceed 64 characters")
        return False
    
    return True

def initialize_firebase():
    """Initialize both Firebase Admin SDKs - one for storage/data and one for auth"""
    global _firebase_app, _auth_firebase_app, _db, _storage_bucket
    
    if _firebase_app and _auth_firebase_app:
        return _db, _storage_bucket
    
    try:
        # Initialize main Firebase (for storage/data)
        if not _firebase_app:
            main_cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
            })
            
            _firebase_app = firebase_admin.initialize_app(main_cred, {
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
                'projectId': os.getenv('FIREBASE_PROJECT_ID')
            }, name='main')
            
            print("Main Firebase app initialized successfully!")
            
            # Initialize Firestore and Storage
            _db = firestore.client(app=_firebase_app)
            _storage_bucket = storage.bucket(app=_firebase_app)
        
        # Initialize Auth Firebase
        if not _auth_firebase_app:
            # Format the auth private key
            auth_private_key = get_formatted_private_key()
            if not auth_private_key:
                raise ValueError("Could not format auth private key")
            
            auth_cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.getenv('AUTH_PROJECT_ID'),
                "private_key_id": os.getenv('AUTH_PRIVATE_KEY_ID'),
                "private_key": auth_private_key,
                "client_email": os.getenv('AUTH_CLIENT_EMAIL'),
                "client_id": os.getenv('AUTH_CLIENT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv('AUTH_CLIENT_CERT_URL')
            })
            
            _auth_firebase_app = firebase_admin.initialize_app(auth_cred, name='auth')
            print("Auth Firebase app initialized successfully!")
        
        return _db, _storage_bucket
        
    except Exception as e:
        print(f"Firebase initialization error: {str(e)}")
        print("Attempting to use default application credentials...")
        try:
            if not _firebase_app:
                _firebase_app = firebase_admin.initialize_app(name='default')
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