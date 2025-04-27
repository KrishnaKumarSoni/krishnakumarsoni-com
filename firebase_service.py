import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Firebase app instance
firebase_app = None

def init_firebase():
    """Initialize Firebase application if not already initialized"""
    global firebase_app
    
    if firebase_app:
        return firebase_app
    
    try:
        # First try to use credentials file if it exists
        if os.path.exists('firebase-credentials.json'):
            # Use service account from file
            cred = credentials.Certificate('firebase-credentials.json')
            logger.info("Using Firebase credentials from firebase-credentials.json file")
        else:
            # Use application default credentials without requiring private key
            # This approach works with the Firebase Web SDK credentials
            project_id = os.getenv('FIREBASE_PROJECT_ID')
            
            if not project_id:
                logger.error("FIREBASE_PROJECT_ID environment variable is required")
                return None
                
            logger.info(f"Initializing Firebase with project ID: {project_id}")
            
            # Initialize with just the project ID
            # This approach doesn't require a service account private key
            firebase_app = firebase_admin.initialize_app(options={
                'projectId': project_id,
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
            })
            
            logger.info("Firebase app initialized successfully without credentials")
            return firebase_app
        
        # If we're using the credentials file approach
        firebase_app = firebase_admin.initialize_app(cred, {
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
        })
        
        logger.info("Firebase app initialized successfully with credentials")
        
        return firebase_app
    
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        return None

def get_firestore_db():
    """Get Firestore database instance"""
    try:
        app = init_firebase()
        if app:
            db = firestore.client()
            logger.info("Firestore connection established")
            return db
        return None
    except Exception as e:
        logger.error(f"Error getting Firestore DB: {str(e)}")
        return None

def check_user_exists(phone_number):
    """
    Check if a user document exists for the given phone number
    
    Args:
        phone_number (str): User's phone number with country code
        
    Returns:
        tuple: (exists (bool), doc_ref (DocumentReference))
    """
    try:
        db = get_firestore_db()
        
        if not db:
            logger.error("Failed to get Firestore database")
            return False, None
        
        # Format document ID from phone number
        doc_id = ''.join(c for c in phone_number if c.isalnum())
        
        # Get document reference
        doc_ref = db.collection('users').document(doc_id)
        
        # Check if document exists
        doc = doc_ref.get()
        
        return doc.exists, doc_ref
    
    except Exception as e:
        logger.error(f"Error checking user existence: {str(e)}")
        return False, None

def save_verification_data(phone_number, browser_data):
    """
    Save user verification data to Firestore.
    If user already exists, update the last_verified_at timestamp.
    If not, create a new document with all verification data.
    
    Args:
        phone_number (str): User's verified phone number with country code
        browser_data (dict): Browser fingerprint data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db = get_firestore_db()
        
        if not db:
            logger.error("Failed to get Firestore database")
            return False
        
        # Check if user document already exists
        exists, doc_ref = check_user_exists(phone_number)
        
        if exists:
            # Update existing document with last_verified_at timestamp
            update_data = {
                'last_verified_at': firestore.SERVER_TIMESTAMP,
                'browser_data': browser_data  # Update browser data too
            }
            
            doc_ref.update(update_data)
            
            logger.info(f"Updated verification timestamp for {phone_number}")
        else:
            # Create a new document with all verification data
            verification_data = {
                'phone_number': phone_number,
                'browser_data': browser_data,
                'created_at': firestore.SERVER_TIMESTAMP,
                'last_verified_at': firestore.SERVER_TIMESTAMP,
                'verified_at': firestore.SERVER_TIMESTAMP
            }
            
            # Format document ID from phone number
            doc_id = ''.join(c for c in phone_number if c.isalnum())
            
            # Set the document
            db.collection('users').document(doc_id).set(verification_data)
            
            logger.info(f"Created new verification document for {phone_number}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving verification data: {str(e)}")
        logger.error(f"Phone: {phone_number}, Browser data: {browser_data}")
        return False 