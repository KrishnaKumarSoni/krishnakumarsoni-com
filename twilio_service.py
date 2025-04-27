import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import random
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Cache to store OTPs temporarily (in a production environment, use Redis or another database)
# Structure: {phone_number: {"otp": "123456", "expires_at": timestamp}}
otp_cache = {}

def generate_otp():
    """Generate a random 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp(phone_number, country_code):
    """
    Send OTP to the specified phone number
    
    Args:
        phone_number (str): The phone number without country code
        country_code (str): The country code with + prefix (e.g., '+91')
        
    Returns:
        dict: Response with status and message
    """
    try:
        # Validate inputs
        if not phone_number or not country_code:
            return {"status": "error", "message": "Phone number and country code are required"}
        
        # Format the phone number with country code
        formatted_phone = f"{country_code}{phone_number}"
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP in cache
        otp_cache[formatted_phone] = {"otp": otp}
        
        # Send SMS with OTP
        message = client.messages.create(
            body=f"Your verification code is: {otp}",
            from_=TWILIO_PHONE_NUMBER,
            to=formatted_phone
        )
        
        logger.info(f"OTP sent to {formatted_phone}. Message SID: {message.sid}")
        
        return {
            "status": "success",
            "message": "OTP sent successfully"
        }
        
    except TwilioRestException as e:
        logger.error(f"Twilio error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to send OTP: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error sending OTP: {str(e)}")
        return {
            "status": "error",
            "message": "An unexpected error occurred"
        }

def verify_otp(phone_number, country_code, otp):
    """
    Verify the OTP for a phone number
    
    Args:
        phone_number (str): The phone number without country code
        country_code (str): The country code with + prefix (e.g., '+91')
        otp (str): The OTP to verify
        
    Returns:
        dict: Response with status and message
    """
    try:
        # Validate inputs
        if not phone_number or not country_code or not otp:
            return {"status": "error", "message": "Phone number, country code, and OTP are required"}
        
        # Format the phone number with country code
        formatted_phone = f"{country_code}{phone_number}"
        
        # Check if OTP exists for this phone number
        if formatted_phone not in otp_cache:
            return {"status": "error", "message": "OTP expired or not sent"}
        
        # Verify OTP
        stored_otp = otp_cache[formatted_phone]["otp"]
        if stored_otp == otp:
            # Clear the OTP from cache after successful verification
            otp_cache.pop(formatted_phone, None)
            
            return {
                "status": "success",
                "message": "OTP verified successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Invalid OTP"
            }
            
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        return {
            "status": "error",
            "message": "An unexpected error occurred"
        }

def resend_otp(phone_number, country_code):
    """
    Resend OTP to the specified phone number
    
    Args:
        phone_number (str): The phone number without country code
        country_code (str): The country code with + prefix (e.g., '+91')
        
    Returns:
        dict: Response with status and message
    """
    try:
        # Simply call the send_otp function
        return send_otp(phone_number, country_code)
        
    except Exception as e:
        logger.error(f"Error resending OTP: {str(e)}")
        return {
            "status": "error",
            "message": "An unexpected error occurred"
        } 