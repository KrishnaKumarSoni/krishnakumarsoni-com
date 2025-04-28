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
    Creates a new user document or updates existing one with verification data.
    
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
        
        # Check if user document already exists
        exists, doc_ref = check_user_exists(phone_number)
        
        if exists:
            # Update existing document with verification data
            update_data = {
                'last_verified_at': now_utc,
                'browser_data': browser_data,
                'updated_at': now_utc
            }
            
            doc_ref.update(update_data)
            logger.info(f"Updated verification data for existing user: {phone_number}")
        else:
            # Create a new user document with verification data
            user_data = {
                'phone_number': phone_number,
                'browser_data': browser_data,
                'created_at': now_utc,
                'last_verified_at': now_utc,
                'verified_at': now_utc,
                'updated_at': now_utc,
                'user_id': doc_id  # Using doc_id as user_id for consistency
            }
            
            db.collection('users').document(doc_id).set(user_data)
            logger.info(f"Created new user with verification data: {phone_number}")
        
        # Verify the operation was successful
        try:
            saved_doc = db.collection('users').document(doc_id).get().to_dict()
            if saved_doc:
                logger.info(f"Verification data saved/updated successfully in users collection")
                return True
            else:
                logger.warning(f"Saved document check returned None")
                return False
        except Exception as read_error:
            logger.warning(f"Could not verify document operation: {str(read_error)}")
            return False
            
    except Exception as e:
        logger.error(f"Error saving verification data: {str(e)}")
        logger.error(f"Phone: {phone_number}")
        return False 