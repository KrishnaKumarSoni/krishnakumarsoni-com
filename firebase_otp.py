"""
Firebase OTP Operations Module
=============================

This module handles OTP-specific Firebase operations, separating these concerns 
from the core Firebase service.

Functions:
---------
- check_user_exists(): Check if a user exists in the database
- save_verification_data(): Save OTP verification data to Firestore

Dependencies:
------------
- firebase_service.py for core Firebase initialization and database access
"""

import logging
from firebase_admin import firestore
from firebase_service import get_firestore_db
import datetime
import pytz  # For timezone handling

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # Format doc_id consistently
        doc_id = ''.join(c for c in phone_number if c.isalnum())
        
        # Use UTC time to ensure consistency across environments
        now_utc = datetime.datetime.now(pytz.UTC)
        current_time = now_utc.isoformat()
        logger.info(f"OTP service saving verification at {current_time} for phone: {phone_number}")
        
        # Check if user document already exists
        exists, doc_ref = check_user_exists(phone_number)
        
        if exists:
            # Update existing document with last_verified_at timestamp
            # Use UTC timestamp instead of local time
            update_data = {
                'last_verified_at': now_utc,
                'browser_data': browser_data,  # Update browser data too
                'updated_at': now_utc
            }
            
            logger.info(f"Updating existing document with UTC timestamp: {now_utc.isoformat()}")
            doc_ref.update(update_data)
            
            # Verify the update was successful by reading back the document
            try:
                updated_doc = doc_ref.get().to_dict()
                if updated_doc:
                    logger.info(f"Updated document in 'users' collection successfully")
                else:
                    logger.warning(f"Updated document check returned None")
            except Exception as read_error:
                logger.warning(f"Could not verify document update: {str(read_error)}")
            
            logger.info(f"Updated verification timestamp for {phone_number}")
        else:
            # Create a new document with all verification data
            verification_data = {
                'phone_number': phone_number,
                'browser_data': browser_data,
                'created_at': now_utc,
                'last_verified_at': now_utc,
                'verified_at': now_utc,
                'updated_at': now_utc
            }
            
            logger.info(f"Creating new document with UTC timestamp: {now_utc.isoformat()}")
            
            # Set the document with explicit timestamps
            db.collection('users').document(doc_id).set(verification_data)
            
            # Verify the document was created by reading it back
            try:
                created_doc = db.collection('users').document(doc_id).get().to_dict()
                if created_doc:
                    logger.info(f"Created document in 'users' collection successfully")
                else:
                    logger.warning(f"Created document check returned None")
            except Exception as read_error:
                logger.warning(f"Could not verify document creation: {str(read_error)}")
            
            logger.info(f"Created new verification document for {phone_number}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving verification data: {str(e)}")
        logger.error(f"Phone: {phone_number}")
        return False 