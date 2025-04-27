"""
Firebase Service Module
======================

This module provides core Firebase initialization and database access for the application
using a singleton pattern. It doesn't implement any feature-specific operations.

Architecture:
------------
1. Initialization: Firebase is initialized once at application startup in app.py
2. Global Instance: The firebase_app global variable maintains a single connection
3. Authentication: Uses Application Default Credentials with Project ID (no service account)

Key Components:
--------------
- init_firebase(): Initialize Firebase with projectId from environment variables
- get_firestore_db(): Get Firestore database client

Usage in Other Modules:
---------------------
- Import core functions:
  from firebase_service import init_firebase, get_firestore_db
- Feature-specific operations should be defined in their own modules:
  - firebase_user.py: User operations
  - firebase_otp.py: OTP verification
  - firebase_blog.py: Blog operations

Error Handling:
--------------
- Each function includes try/except blocks and returns None on failure
- Always check return values before using results
- For best practices, see FIREBASE_ARCHITECTURE.md

Environment Variables:
--------------------
- FIREBASE_PROJECT_ID: Required for initialization
- FIREBASE_STORAGE_BUCKET: Required for Storage bucket access

See FIREBASE_ARCHITECTURE.md for detailed architecture and extension recommendations.
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import logging
import datetime
from dotenv import load_dotenv
import pytz  # For timezone handling

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
    
    # Return existing instance if already initialized
    if firebase_app:
        logger.info("Reusing existing Firebase instance")
        return firebase_app
    
    try:
        # Get project ID from environment
        project_id = os.getenv('FIREBASE_PROJECT_ID')
        
        if not project_id:
            logger.error("FIREBASE_PROJECT_ID environment variable is required")
            return None
        
        logger.info(f"Initializing Firebase with project ID: {project_id}")
        
        # Try to initialize with credentials file if it exists
        cred = None
        cred_file = 'temp_firebase_credentials.json'
        
        if os.path.exists(cred_file):
            try:
                # Check if the file has valid credentials (not null values)
                with open(cred_file, 'r') as f:
                    cred_data = json.load(f)
                
                # Log available credential components for debugging
                logger.info(f"Firebase credentials available: PROJECT_ID={bool(cred_data.get('project_id'))}, CLIENT_EMAIL={bool(cred_data.get('client_email') and cred_data.get('private_key'))}")
                
                # Only use credentials file if it has valid private_key that's not null
                if cred_data.get('private_key') and cred_data.get('private_key') != "null" and cred_data.get('client_email'):
                    logger.info("Using credentials from temp_firebase_credentials.json")
                    cred = credentials.Certificate(cred_file)
                else:
                    logger.warning("Credentials file exists but has null or missing values, using project ID only")
            except Exception as cred_error:
                logger.warning(f"Could not load credentials file: {str(cred_error)}")
        
        # Initialize with credentials if available, otherwise just project ID
        if cred:
            firebase_app = firebase_admin.initialize_app(cred, options={
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
            })
            logger.info("Firebase app initialized successfully with credentials")
        else:
            # Initialize with just project ID - for environments that support ADC
            firebase_app = firebase_admin.initialize_app(options={
                'projectId': project_id,
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
            })
            logger.info("Firebase app initialized successfully without credentials")
        
        return firebase_app
        
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        # Add more detailed error information
        if "Failed to convert certificate credential to bytes" in str(e):
            logger.error("The credentials file appears to be invalid or corrupted.")
            logger.error("Please check your credentials file or environment variables.")
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

def save_verification_data(phone_number, browser_data=None):
    """
    Save phone verification data to Firestore
    
    Args:
        phone_number (str): The verified phone number with country code
        browser_data (dict): Optional browser/device information
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db = get_firestore_db()
        if not db:
            logger.error("Failed to get Firestore DB for saving verification data")
            return False
        
        # Use UTC time to ensure consistency across environments
        now_utc = datetime.datetime.now(pytz.UTC)
        current_time = now_utc.isoformat()
        logger.info(f"Firebase service saving verification at {current_time} for phone: {phone_number}")
        
        # Create a document with verification timestamp and data (using UTC)
        verification_data = {
            'phone_number': phone_number,
            'verified_at': now_utc,
            'browser_data': browser_data or {},
            'updated_at': now_utc,
            'last_verified_at': now_utc
        }
        
        # Format phone number for document ID to ensure consistency
        doc_id = ''.join(c for c in phone_number if c.isalnum())
        
        # Save to a collection called 'verified_phones' with consistent document ID
        db.collection('verified_phones').document(doc_id).set(
            verification_data, merge=True
        )
        
        # Verify the update was successful by reading back
        try:
            saved_data = db.collection('verified_phones').document(doc_id).get().to_dict()
            if saved_data:
                logger.info(f"Verification data saved successfully to 'verified_phones' collection")
            else:
                logger.warning(f"Saved data returned None from 'verified_phones' collection")
        except Exception as read_error:
            logger.warning(f"Could not verify saved data: {str(read_error)}")
        
        logger.info(f"Successfully saved verification data for {phone_number}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving verification data: {str(e)}")
        return False 