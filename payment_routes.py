from flask import Blueprint, request, jsonify
from qrcode_service import generate_upi_qr_code
from firebase_service import check_user_exists
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint for payment routes
payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

# UPI ID for payments (in a production app, this would come from a database or config)
DEFAULT_UPI_ID = "9166900151@ptsbi"
DEFAULT_MERCHANT_NAME = "Krishna Kumar Soni"

@payment_bp.route('/generate-qr', methods=['POST'])
def generate_payment_qr():
    """
    Generate a UPI payment QR code
    
    Request JSON:
    {
        "amount": 1000.50, (required)
        "phone_number": "+919876543210", (required)
        "browser_data": {...}, (required)
        "merchant_name": "Company Name", (optional)
        "transaction_note": "Payment for XYZ" (optional)
    }
    """
    data = request.json
    
    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid request data"
        }), 400
    
    # Validate required fields
    if 'amount' not in data:
        return jsonify({
            "status": "error",
            "message": "Amount is required"
        }), 400
    
    if 'phone_number' not in data:
        return jsonify({
            "status": "error", 
            "message": "Phone number is required"
        }), 400
    
    if 'browser_data' not in data:
        return jsonify({
            "status": "error",
            "message": "Browser data is required"
        }), 400
    
    # Get payment details
    amount = data.get('amount')
    phone_number = data.get('phone_number')
    browser_data = data.get('browser_data')
    merchant_name = data.get('merchant_name', DEFAULT_MERCHANT_NAME)
    transaction_note = data.get('transaction_note', f"Payment for order")
    
    # Log the incoming request data for debugging
    logger.info(f"Received QR generation request for phone: {phone_number}, amount: {amount}")
    
    # Ensure phone_number is properly formatted (has country code)
    if not phone_number.startswith('+'):
        phone_number = f"+{phone_number}"
    
    # Check for verification cookie - just for logging info, don't update Firebase
    verified_phone = request.cookies.get('verified_phone')
    if verified_phone and verified_phone == phone_number:
        logger.info(f"QR generated for verified phone: {phone_number}")
    
    # Generate QR code
    try:
        qr_code_data = generate_upi_qr_code(
            upi_id=DEFAULT_UPI_ID,
            amount=amount,
            merchant_name=merchant_name,
            transaction_note=transaction_note
        )
        
        if not qr_code_data:
            return jsonify({
                "status": "error",
                "message": "Failed to generate QR code"
            }), 500
        
        # Generate UPI URL
        upi_url = f"upi://pay?pa={DEFAULT_UPI_ID}"
        if amount:
            upi_url += f"&am={amount}"
        if merchant_name:
            upi_url += f"&pn={merchant_name}"
        if transaction_note:
            upi_url += f"&tn={transaction_note}"
        
        return jsonify({
            "status": "success",
            "qr_code": qr_code_data,
            "upi_details": {
                "upi_id": DEFAULT_UPI_ID,
                "upi_url": upi_url,
                "amount": amount,
                "merchant_name": merchant_name,
                "transaction_note": transaction_note
            }
        }), 200
    except Exception as e:
        logger.error(f"Error in generate_payment_qr: {str(e)}")
        
        # Basic error response
        return jsonify({
            "status": "error",
            "message": f"Failed to generate QR code: {str(e)}"
        }), 500

def init_payment_routes(app):
    """Register the blueprint with the Flask app"""
    app.register_blueprint(payment_bp) 