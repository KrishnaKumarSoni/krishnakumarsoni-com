#!/usr/bin/env python3
"""
Helper script to generate a Firebase credentials file from environment variables.
Run this script before starting your application to create the credentials file.
"""

import os
import json
from dotenv import load_dotenv

def generate_credentials_file():
    # Load environment variables
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = [
        'AUTH_PROJECT_ID', 
        'AUTH_PRIVATE_KEY_ID', 
        'AUTH_PRIVATE_KEY', 
        'AUTH_CLIENT_EMAIL',
        'AUTH_CLIENT_ID',
        'AUTH_CLIENT_CERT_URL'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        return False
    
    # Process private key - replace literal \n with actual newlines
    private_key = os.getenv('AUTH_PRIVATE_KEY')
    if '\\n' in private_key:
        private_key = private_key.replace('\\n', '\n')
    
    # Create service account info dictionary
    service_account_info = {
        "type": "service_account",
        "project_id": os.getenv('AUTH_PROJECT_ID'),
        "private_key_id": os.getenv('AUTH_PRIVATE_KEY_ID'),
        "private_key": private_key,
        "client_email": os.getenv('AUTH_CLIENT_EMAIL'),
        "client_id": os.getenv('AUTH_CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv('AUTH_CLIENT_CERT_URL')
    }
    
    # Write to JSON file
    output_file = 'firebase-credentials.json'
    with open(output_file, 'w') as f:
        json.dump(service_account_info, f, indent=2)
    
    print(f"Credentials file generated at: {output_file}")
    return True

if __name__ == "__main__":
    if generate_credentials_file():
        print("✅ Firebase credentials file created successfully!")
    else:
        print("❌ Failed to create Firebase credentials file.") 