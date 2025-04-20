import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage
import google.cloud.firestore

# Load environment variables
load_dotenv()

# Debug: Print environment variables
print("Environment variables loaded")

# Singleton pattern for blog Firebase app
_blog_firebase_app = None
_blog_db = None
_blog_storage_bucket = None

def get_formatted_private_key(key):
    """Format private key with proper line breaks and structure"""
    if not key:
        print("Warning: No private key found in environment variables")
        return None
        
    # Strip any wrapping quotes and whitespace
    key = key.strip().strip('"\'')
    
    # Add header and footer if not present
    if not key.startswith('-----BEGIN PRIVATE KEY-----'):
        key = '-----BEGIN PRIVATE KEY-----\n' + key
    if not key.endswith('-----END PRIVATE KEY-----'):
        key = key + '\n-----END PRIVATE KEY-----'
        
    # Ensure proper line breaks
    parts = key.split('-----')
    if len(parts) >= 4:  # Has both header and footer
        base64_content = parts[2].strip()
        # Split into 64-char chunks and join with newlines
        chunks = [base64_content[i:i+64] for i in range(0, len(base64_content), 64)]
        formatted_content = '\n'.join(chunks)
        key = f"-----BEGIN PRIVATE KEY-----\n{formatted_content}\n-----END PRIVATE KEY-----\n"
    
    # Debug output
    lines = key.split('\n')
    print(f"\nPrivate key format check:")
    print(f"Number of lines: {len(lines)}")
    print(f"First line: {lines[0]}")
    print(f"Last line: {lines[-1]}")
    print(f"Middle lines length range: {min(len(l) for l in lines[1:-1] if l)} - {max(len(l) for l in lines[1:-1] if l)}")
    
    return key

def initialize_firebase_database():
    """Initialize Firebase for blog database operations"""
    global _blog_firebase_app, _blog_db, _blog_storage_bucket
    
    try:
        # Check if already initialized
        try:
            _blog_firebase_app = firebase_admin.get_app('blog')
            return _blog_firebase_app, _blog_db, _blog_storage_bucket
        except ValueError:
            pass  # App not initialized yet
            
        # Get database config for blog operations
        creds = {
            'type': 'service_account',
            'project_id': os.getenv('AUTH_PROJECT_ID'),
            'private_key_id': os.getenv('AUTH_PRIVATE_KEY_ID'),
            'private_key': get_formatted_private_key(os.getenv('AUTH_PRIVATE_KEY')),
            'client_email': os.getenv('AUTH_CLIENT_EMAIL'),
            'client_id': os.getenv('AUTH_CLIENT_ID', ''),
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            'client_x509_cert_url': os.getenv('AUTH_CLIENT_CERT_URL')
        }
        
        # Debug output
        print("\nBlog Firebase Credentials Status:")
        for key in ['project_id', 'private_key_id', 'client_email', 'client_x509_cert_url']:
            print(f"{key}: {'Present' if creds.get(key) else 'Missing'}")
        print(f"private_key: {'Present and formatted' if creds.get('private_key') else 'Missing'}")
        
        # Initialize Firebase app for blog
        cert = credentials.Certificate(creds)
        _blog_firebase_app = firebase_admin.initialize_app(
            cert,
            {
                'storageBucket': os.getenv('AUTH_STORAGE_BUCKET')
            },
            name='blog'
        )
        
        # Initialize blog services
        _blog_db = firestore.client(app=_blog_firebase_app)
        _blog_storage_bucket = storage.bucket(app=_blog_firebase_app)
        
        print("Blog Firebase initialized successfully")
        return _blog_firebase_app, _blog_db, _blog_storage_bucket
        
    except Exception as e:
        print(f"Error initializing blog Firebase: {str(e)}")
        return None

# Initialize Firebase database for blog
try:
    result = initialize_firebase_database()
    if result:
        app, db, storage_bucket = result
    else:
        print("Warning: Blog Firebase initialization failed")
        db = None
        storage_bucket = None
except Exception as e:
    print(f"Error in blog initialization: {str(e)}")
    db = None
    storage_bucket = None

# Export blog services for use in other modules
__all__ = ['db', 'storage_bucket'] 