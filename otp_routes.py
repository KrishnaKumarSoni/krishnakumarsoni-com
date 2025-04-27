from flask import Blueprint, request, jsonify, make_response
from twilio_service import send_otp, verify_otp, resend_otp
from firebase_service import save_verification_data
import logging
import datetime
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint for OTP routes
otp_bp = Blueprint('otp', __name__, url_prefix='/api/otp')

@otp_bp.route('/send', methods=['POST'])
def send_otp_route():
    """
    Send OTP to the phone number
    
    Request JSON:
    {
        "phone_number": "1234567890",
        "country_code": "+91"
    }
    """
    data = request.json
    
    if not data or 'phone_number' not in data or 'country_code' not in data:
        return jsonify({
            "status": "error",
            "message": "Phone number and country code are required"
        }), 400
    
    # Call the send_otp function from twilio_service
    response = send_otp(data['phone_number'], data['country_code'])
    
    if response['status'] == 'error':
        return jsonify(response), 400
    
    return jsonify(response), 200

@otp_bp.route('/verify', methods=['POST'])
def verify_otp_route():
    """
    Verify OTP for a phone number
    
    Request JSON:
    {
        "phone_number": "1234567890",
        "country_code": "+91",
        "otp": "123456",
        "browser_data": {...} (optional)
    }
    """
    data = request.json
    
    if not data or 'phone_number' not in data or 'country_code' not in data or 'otp' not in data:
        return jsonify({
            "status": "error",
            "message": "Phone number, country code, and OTP are required"
        }), 400
    
    # Call the verify_otp function from twilio_service
    response = verify_otp(data['phone_number'], data['country_code'], data['otp'])
    
    if response['status'] == 'error':
        return jsonify(response), 400
    
    # Format the full phone number
    formatted_phone = f"{data['country_code']}{data['phone_number']}"
    
    # Extract browser data if provided
    browser_data = data.get('browser_data', {})
    
    # Add verification time to the browser data for debugging
    browser_data['verification_time'] = datetime.datetime.now().isoformat()
    
    # Log the verification time
    logger.info(f"OTP verified at {browser_data['verification_time']} for {formatted_phone}")
    
    # Create a flag to track Firebase operation success
    firebase_success = False
    
    # Save verification data to Firebase in a non-blocking way - but with an event to track completion
    verification_complete_event = threading.Event()
    
    def save_data_async():
        nonlocal firebase_success
        try:
            # First try to save with the OTP-specific function
            from firebase_otp import save_verification_data as save_otp_data
            otp_success = save_otp_data(formatted_phone, browser_data)
            
            # Also save with the general firebase service function as backup
            from firebase_service import save_verification_data as save_general_data
            general_success = save_general_data(formatted_phone, browser_data)
            
            firebase_success = otp_success or general_success
            
            if not firebase_success:
                logger.warning(f"Both Firebase save operations failed for {formatted_phone}")
            else:
                logger.info(f"Firebase verification data saved successfully for {formatted_phone}")
                
        except Exception as e:
            logger.error(f"Error saving verification data: {str(e)}")
        finally:
            # Signal that the verification has been attempted (success or failure)
            verification_complete_event.set()
    
    # Start a thread to handle Firebase operations asynchronously
    save_thread = threading.Thread(target=save_data_async)
    save_thread.daemon = True  # Make it a daemon thread so it doesn't block app shutdown
    save_thread.start()
    
    # Wait for a short time for the Firebase operation to complete (max 5 seconds)
    # This helps ensure the data is actually saved without making the user wait too long
    verification_complete = verification_complete_event.wait(timeout=5.0)
    
    if verification_complete:
        if firebase_success:
            logger.info(f"Firebase verification completed successfully for {formatted_phone}")
        else:
            logger.warning(f"Firebase verification completed but reported failure for {formatted_phone}")
    else:
        logger.warning(f"Firebase verification timed out for {formatted_phone} - continuing with response")
    
    # Create response with verification cookie
    resp = make_response(jsonify(response))
    
    # Set a cookie to remember the verified phone number
    # Set to expire in 30 days (or adjust as needed)
    expires = datetime.datetime.now() + datetime.timedelta(days=30)
    resp.set_cookie('verified_phone', 
                    formatted_phone, 
                    expires=expires, 
                    httponly=True, 
                    secure=False,  # Set to True in production with HTTPS
                    samesite='Lax')
    
    return resp, 200

@otp_bp.route('/resend', methods=['POST'])
def resend_otp_route():
    """
    Resend OTP to the phone number
    
    Request JSON:
    {
        "phone_number": "1234567890",
        "country_code": "+91"
    }
    """
    data = request.json
    
    if not data or 'phone_number' not in data or 'country_code' not in data:
        return jsonify({
            "status": "error",
            "message": "Phone number and country code are required"
        }), 400
    
    # Call the resend_otp function from twilio_service
    response = resend_otp(data['phone_number'], data['country_code'])
    
    if response['status'] == 'error':
        return jsonify(response), 400
    
    return jsonify(response), 200

@otp_bp.route('/check-verification', methods=['GET'])
def check_verification_route():
    """Check if user has a valid verification cookie"""
    # Get the verification cookie
    verified_phone = request.cookies.get('verified_phone')
    
    if not verified_phone:
        return jsonify({
            "status": "error",
            "message": "Not verified",
            "verified": False
        }), 200  # Return 200 even though not verified
    
    return jsonify({
        "status": "success",
        "message": "Phone number verified",
        "verified": True,
        "phone": verified_phone
    }), 200

def init_otp_routes(app):
    """Register the blueprint with the Flask app"""
    app.register_blueprint(otp_bp) 