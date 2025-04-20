#!/usr/bin/env python3
"""
Verify environment variables for Vercel deployment.
Run this script to check if all required environment variables are properly set.
"""

import os
from dotenv import load_dotenv

def verify_firebase_config():
    """Verify Firebase configuration variables"""
    # Load environment variables
    load_dotenv()
    
    # Required Firebase variables
    firebase_vars = {
        'Storage Config': [
            'FIREBASE_API_KEY',
            'FIREBASE_PROJECT_ID',
            'FIREBASE_AUTH_DOMAIN',
            'FIREBASE_STORAGE_BUCKET',
            'FIREBASE_MESSAGING_SENDER_ID',
            'FIREBASE_APP_ID',
            'FIREBASE_MEASUREMENT_ID'
        ],
        'Auth Config': [
            'AUTH_PROJECT_ID',
            'AUTH_PRIVATE_KEY_ID',
            'AUTH_PRIVATE_KEY',
            'AUTH_CLIENT_EMAIL',
            'AUTH_CLIENT_ID',
            'AUTH_CLIENT_CERT_URL'
        ]
    }
    
    all_valid = True
    
    print("\n🔍 Checking environment variables for Vercel deployment...\n")
    
    for section, vars in firebase_vars.items():
        print(f"\n📋 {section}:")
        for var in vars:
            value = os.getenv(var)
            if not value:
                print(f"❌ {var}: Missing")
                all_valid = False
            else:
                # Special handling for private key
                if var == 'AUTH_PRIVATE_KEY':
                    if '-----BEGIN PRIVATE KEY-----' in value:
                        key_format = "Valid format"
                        status = "✅"
                    else:
                        key_format = "Invalid format"
                        status = "❌"
                        all_valid = False
                    print(f"{status} {var}: {key_format}")
                else:
                    # Mask the actual values for security
                    masked_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
                    print(f"✅ {var}: {masked_value}")
    
    print("\n📝 Summary:")
    if all_valid:
        print("✅ All environment variables are properly set for Vercel deployment!")
    else:
        print("❌ Some environment variables are missing or invalid.")
        print("\n⚠️ Action Required:")
        print("1. Make sure all missing variables are added to your Vercel project's environment variables")
        print("2. For AUTH_PRIVATE_KEY, ensure it:")
        print("   - Starts with '-----BEGIN PRIVATE KEY-----'")
        print("   - Contains proper line breaks")
        print("   - Ends with '-----END PRIVATE KEY-----'")
        print("3. Double-check all values in the Vercel dashboard")
    
    return all_valid

if __name__ == "__main__":
    verify_firebase_config() 