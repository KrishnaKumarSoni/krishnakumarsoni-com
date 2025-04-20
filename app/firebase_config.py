import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Load environment variables
load_dotenv()

# Debug: Print blog Firebase config status
print("\nBlog Firebase Config Status:")
print(f"API Key: {'Present' if os.getenv('FIREBASE_API_KEY') else 'Missing'}")
print(f"Project ID: {'Present' if os.getenv('FIREBASE_PROJECT_ID') else 'Missing'}")
print(f"Storage Bucket: {'Present' if os.getenv('FIREBASE_STORAGE_BUCKET') else 'Missing'}")

# Singleton pattern for blog Firebase app
_blog_firebase_app = None
_blog_db = None
_blog_storage_bucket = None

def initialize_firebase():
    """Initialize Firebase for blog database operations"""
    global _blog_firebase_app, _blog_db, _blog_storage_bucket
    
    try:
        # Check if already initialized
        try:
            _blog_firebase_app = firebase_admin.get_app('blog')
            return _blog_db, _blog_storage_bucket
        except ValueError:
            pass
            
        # Initialize Firebase Admin SDK for blog operations
        # For blog, we only need basic config without private key
        cred = credentials.ApplicationDefault()
        _blog_firebase_app = firebase_admin.initialize_app(cred, {
            'projectId': os.getenv('FIREBASE_PROJECT_ID'),
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
        }, name='blog')
        
        print("Blog Firebase initialized successfully")
        
        # Initialize Firestore and Storage
        _blog_db = firestore.client(app=_blog_firebase_app)
        _blog_storage_bucket = storage.bucket(app=_blog_firebase_app)
        
        return _blog_db, _blog_storage_bucket
        
    except Exception as e:
        print(f"Error initializing blog Firebase: {str(e)}")
        return None, None

# Initialize Firebase and export the database and storage bucket
db, storage_bucket = initialize_firebase()

# Export for use in other modules
__all__ = ['db', 'storage_bucket'] 