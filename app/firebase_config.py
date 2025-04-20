import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth

# Load environment variables
load_dotenv()

# Debug: Print environment variables
print("Environment variables:")
print(f"FIREBASE_STORAGE_BUCKET: {os.getenv('FIREBASE_STORAGE_BUCKET')}")
print(f"FIREBASE_PROJECT_ID: {os.getenv('FIREBASE_PROJECT_ID')}")

# Singleton pattern for Firebase
_firebase_app = None
_db = None
_storage_bucket = None

def initialize_firebase():
    global _firebase_app, _db, _storage_bucket
    
    if _firebase_app is not None:
        return _db, _storage_bucket
        
    try:
        _firebase_app = firebase_admin.initialize_app(
            credentials.Certificate({
                "type": "service_account",
                "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                "private_key_id": os.getenv('AUTH_PRIVATE_KEY_ID'),
                "private_key": os.getenv('AUTH_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('AUTH_CLIENT_EMAIL'),
                "client_id": os.getenv('AUTH_CLIENT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv('AUTH_CLIENT_CERT_URL')
            }),
            {
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
                'projectId': os.getenv('FIREBASE_PROJECT_ID')
            }
        )
        
        _db = firestore.client()
        _storage_bucket = storage.bucket()
        
        return _db, _storage_bucket
    except Exception as e:
        print(f"Firebase initialization error: {str(e)}")
        raise e

# Export initialized instances
db, storage_bucket = initialize_firebase()

# Export for use in other modules
__all__ = ['db', 'storage_bucket', 'auth'] 