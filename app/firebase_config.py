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
            
        # Debug raw key
        print("\nRaw Key Debug:")
        print(f"Raw key length: {len(key)}")
        print(f"Raw key starts with: {key[:50]}")
        print(f"Raw key contains \\n: {'\\n' in key}")
        print(f"Raw key contains quotes: {'"' in key}")
            
        # Strip any wrapping quotes and whitespace
        key = key.strip().strip('"\'')
        
        # Define header and footer
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        
        # Extract base64 content
        if header in key and footer in key:
            # Get content between header and footer
            start = key.index(header) + len(header)
            end = key.index(footer)
            base64_content = key[start:end].strip()
        else:
            # If no header/footer, assume entire content is base64
            base64_content = key.replace(header, '').replace(footer, '').strip()
        
        # Clean up base64 content - remove all whitespace and newlines
        base64_content = ''.join(base64_content.split())
        
        # Format key with proper line breaks
        formatted_lines = [header]
        
        # Split base64 into 64-character chunks
        for i in range(0, len(base64_content), 64):
            chunk = base64_content[i:i+64]
            formatted_lines.append(chunk)
            
        formatted_lines.append(footer)
        
        # Join with newlines, ensuring proper spacing
        formatted_key = '\n'.join(formatted_lines) + '\n'
        
        # Debug output
        print("\nFormatted Key Debug:")
        lines = formatted_key.split('\n')
        print(f"Formatted key has {len(lines)} lines")
        print(f"Header present: {formatted_key.startswith(header)}")
        print(f"Footer present: {formatted_key.endswith(footer + '\n')}")
        print(f"Line lengths:")
        for i, line in enumerate(lines):
            if line and i > 0 and i < len(lines) - 1:  # Skip header/footer
                print(f"Line {i}: {len(line)} characters")
        
        return formatted_key
        
    except Exception as e:
        print(f"Error formatting private key: {str(e)}")
        return None

def get_database_credentials():
    """Get credentials for database Firebase project"""
    private_key = get_formatted_private_key()
    if not private_key:
        print("Failed to get formatted private key")
        return None
        
    # Debug the key format
    print("\nPrivate Key Debug:")
    lines = private_key.split('\n')
    print(f"Number of lines: {len(lines)}")
    print(f"First line: {lines[0]}")
    print(f"Last non-empty line: {[line for line in lines if line][-1]}")
        
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

def initialize_firebase():
    """Initialize Firebase with service account credentials - for backward compatibility"""
    return initialize_firebase_database()

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
__all__ = ['db', 'storage_bucket', 'get_formatted_private_key', 'initialize_firebase'] 