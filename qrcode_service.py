import segno
import os
from PIL import Image, ImageDraw
from io import BytesIO
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_upi_qr_code(upi_id, amount=None, merchant_name=None, transaction_note=None):
    """
    Generate a beautiful UPI payment QR code with Segno
    
    Args:
        upi_id (str): UPI ID for payment
        amount (float, optional): Payment amount
        merchant_name (str, optional): Merchant name
        transaction_note (str, optional): Transaction note
        
    Returns:
        str: Base64 encoded QR code image
    """
    try:
        # Build UPI URL
        upi_url = f"upi://pay?pa={upi_id}"
        
        if amount:
            upi_url += f"&am={amount}"
        
        if merchant_name:
            upi_url += f"&pn={merchant_name}"
            
        if transaction_note:
            upi_url += f"&tn={transaction_note}"
        
        # Log the UPI URL for debugging
        logger.info(f"Generated UPI URL: {upi_url}")
        
        # Simply use Segno to generate QR with rounded modules
        qr = segno.make(upi_url, error='h')
        
        # Get the QR code directly as a base64 encoded PNG
        buffered = BytesIO()
        qr.save(buffered, kind='png', scale=10, dark='#D35400', light='white', border=2)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        return None 