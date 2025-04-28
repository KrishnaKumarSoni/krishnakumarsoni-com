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
    Save phone verification data to Firestore users collection
    
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
        
        # Format doc_id consistently
        doc_id = ''.join(c for c in phone_number if c.isalnum())
        
        # Create a document with verification timestamp and data
        verification_data = {
            'phone_number': phone_number,
            'verified_at': now_utc,
            'browser_data': browser_data or {},
            'updated_at': now_utc,
            'last_verified_at': now_utc
        }
        
        # Save to users collection with merge=True to not overwrite existing data
        db.collection('users').document(doc_id).set(
            verification_data, merge=True
        )
        
        # Verify the update was successful by reading back
        try:
            saved_data = db.collection('users').document(doc_id).get().to_dict()
            if saved_data:
                logger.info(f"Verification data saved successfully to 'users' collection")
            else:
                logger.warning(f"Saved data returned None from 'users' collection")
        except Exception as read_error:
            logger.warning(f"Could not verify saved data: {str(read_error)}")
        
        return True
    except Exception as e:
        logger.error(f"Error saving verification data: {str(e)}")
        return False

def find_recent_transaction(phone_number, minutes=5):
    """
    Find a recent transaction for the given phone number within the specified time window
    
    Args:
        phone_number (str): User's phone number with country code
        minutes (int): Time window in minutes to look for recent transactions
        
    Returns:
        tuple: (found (bool), transaction_data (dict), transaction_id (str))
    """
    try:
        db = get_firestore_db()
        if not db:
            logger.error("Failed to get Firestore DB for finding recent transactions")
            return False, None, None
        
        # Calculate time threshold (current time - minutes)
        now_utc = datetime.datetime.now(pytz.UTC)
        threshold_time = now_utc - datetime.timedelta(minutes=minutes)
        
        # First, get all recent transactions for this phone number
        # This avoids the need for a composite index by using a simpler query
        transactions_ref = db.collection('live-transactions')
        # Use the standard where syntax
        query = transactions_ref.where('phone_number', '==', phone_number)
        
        # Execute query
        results = query.get()
        
        # Check results manually to find the most recent valid transaction
        most_recent_transaction = None
        most_recent_transaction_id = None
        most_recent_time = None
        
        for doc in results:
            transaction_data = doc.to_dict()
            
            # Skip if payment is already received
            if transaction_data.get('payment_received', False):
                continue
                
            # Skip if created_at is missing or not a timestamp
            created_at = transaction_data.get('created_at')
            if not created_at or not isinstance(created_at, datetime.datetime):
                continue
                
            # Skip if older than threshold time
            if created_at < threshold_time:
                continue
                
            # Check if this is more recent than our current most recent
            if most_recent_time is None or created_at > most_recent_time:
                most_recent_transaction = transaction_data
                most_recent_transaction_id = doc.id
                most_recent_time = created_at
        
        # If we found a transaction, return it
        if most_recent_transaction:
            logger.info(f"Found recent transaction for {phone_number}: {most_recent_transaction_id}")
            return True, most_recent_transaction, most_recent_transaction_id
        
        logger.info(f"No recent transactions found for {phone_number} within last {minutes} minutes")
        return False, None, None
        
    except Exception as e:
        logger.error(f"Error finding recent transactions: {str(e)}")
        return False, None, None

def save_live_transaction(phone_number, amount, browser_data=None):
    """
    Save live transaction data to Firestore when a QR code is generated
    First checks if a recent transaction exists and updates it if found
    
    Args:
        phone_number (str): User's phone number with country code
        amount (float): Transaction amount
        browser_data (dict): Optional browser/device information
    
    Returns:
        tuple: (success (bool), transaction_id (str), is_new (bool))
    """
    try:
        db = get_firestore_db()
        if not db:
            logger.error("Failed to get Firestore DB for saving live transaction data")
            return False, None, False
        
        # Check for recent transactions in the last 5 minutes
        found, transaction_data, transaction_id = find_recent_transaction(phone_number, minutes=5)
        
        # Use UTC time for consistency
        now_utc = datetime.datetime.now(pytz.UTC)
        
        # If we found a transaction, update it instead of creating a new one
        if found and transaction_data:
            # Update existing transaction
            db.collection('live-transactions').document(transaction_id).update({
                'last_qr_gen_at': now_utc,
                'amount': float(amount),  # Update amount in case it changed
                'browser_data': browser_data or {},
                'updated_at': now_utc
            })
            
            logger.info(f"Updated existing transaction {transaction_id} for phone: {phone_number}")
            return True, transaction_id, False
        
        # No recent transaction found, create a new one
        # Format phone number for consistency and part of the transaction ID
        clean_phone = ''.join(c for c in phone_number if c.isalnum())
        
        # Generate a unique transaction ID
        import uuid
        transaction_id = f"{clean_phone}_{int(now_utc.timestamp())}_{uuid.uuid4().hex[:8]}"
        
        # Check if user exists and get user ID if available
        exists, user_doc_ref = None, None
        try:
            from firebase_otp import check_user_exists
            exists, user_doc_ref = check_user_exists(phone_number)
        except Exception as user_check_error:
            logger.warning(f"Error checking user existence: {str(user_check_error)}")
        
        # Get user ID if available, otherwise use phone number
        user_id = None
        if exists and user_doc_ref:
            try:
                user_data = user_doc_ref.get().to_dict()
                user_id = user_data.get('user_id', clean_phone)
            except Exception as user_data_error:
                logger.warning(f"Error getting user data: {str(user_data_error)}")
        
        # If no user ID available, use phone number as ID
        if not user_id:
            user_id = clean_phone
        
        # Create transaction data
        transaction_data = {
            'transaction_id': transaction_id,
            'user_id': user_id,
            'phone_number': phone_number,
            'amount': float(amount),
            'last_qr_gen_at': now_utc,
            'created_at': now_utc,
            'status': 'pending',
            'browser_data': browser_data or {},
            'payment_received': False,
            'payment_verified': False,
            'updated_at': now_utc
        }
        
        # Save to live-transactions collection
        db.collection('live-transactions').document(transaction_id).set(transaction_data)
        
        logger.info(f"New live transaction created with ID: {transaction_id} for phone: {phone_number}")
        return True, transaction_id, True
    except Exception as e:
        logger.error(f"Error saving live transaction data: {str(e)}")
        return False, None, False

def update_transaction_qr_timestamp(transaction_id):
    """
    Update the last_qr_gen_at timestamp for a live transaction when QR is refreshed
    
    Args:
        transaction_id (str): The transaction ID to update
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db = get_firestore_db()
        if not db:
            logger.error("Failed to get Firestore DB for updating transaction timestamp")
            return False
        
        # Use UTC time to ensure consistency across environments
        now_utc = datetime.datetime.now(pytz.UTC)
        
        # Update only the timestamp field
        db.collection('live-transactions').document(transaction_id).update({
            'last_qr_gen_at': now_utc
        })
        
        logger.info(f"Updated last_qr_gen_at for transaction: {transaction_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating transaction timestamp: {str(e)}")
        return False 