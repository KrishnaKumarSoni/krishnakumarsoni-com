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

def initialize_firebase():
    """
    Initialize Firebase Admin SDK for main project (storage/firestore).
    Returns a tuple of (firestore_db, storage_bucket)
    """
    try:
        # Check if main app is already initialized
        app = firebase_admin.get_app()
        print("Main Firebase app already initialized")
    except ValueError:
        # Initialize main Firebase app with environment variables
        config = {
            'apiKey': os.getenv('FIREBASE_API_KEY'),
            'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
            'projectId': os.getenv('FIREBASE_PROJECT_ID'),
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
            'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
            'appId': os.getenv('FIREBASE_APP_ID'),
            'measurementId': os.getenv('FIREBASE_MEASUREMENT_ID')
        }
        
        firebase_admin.initialize_app(options=config)
        print("Main Firebase app initialized successfully")

    try:
        # Initialize Firestore and Storage
        db = firestore.client()
        bucket = storage.bucket()
        return db, bucket
    except Exception as e:
        print(f"Error initializing Firebase services: {str(e)}")
        raise

# Initialize Firebase services
db, storage_bucket = initialize_firebase()

# Export for use in other modules
__all__ = ['db', 'storage_bucket', 'auth'] 