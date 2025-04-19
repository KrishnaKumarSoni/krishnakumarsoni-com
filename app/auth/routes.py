from flask import Blueprint, request, jsonify, session
from functools import wraps
from app.auth.firebase import (
    start_phone_verification,
    verify_phone_otp,
    check_auth
)
from app.firebase_config import auth

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session-based authentication
        if check_auth():
            return f(*args, **kwargs)
        
        # Check token-based authentication as fallback
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            # Extract the token
            token = auth_header.split('Bearer ')[1]
            
            # For session-based tokens, format is "session-auth:phone:timestamp"
            if token.startswith('session-auth:'):
                parts = token.split(':')
                if len(parts) == 3:
                    phone = parts[1]
                    # Verify against session
                    user = session.get('user', {})
                    if user.get('phone_number') == phone and user.get('is_verified'):
                        request.user = user
                        return f(*args, **kwargs)
            
            return jsonify({'error': 'Invalid or expired token'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401
            
    return decorated_function

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth_status():
    """Check if user is authenticated and return their auth state"""
    if check_auth():
        user = session.get('user', {})
        return jsonify({
            'authenticated': True,
            'phone_number': user.get('phone_number'),
            'auth_time': user.get('auth_time')
        })
    return jsonify({'authenticated': False})

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone_number = data.get('phone_number')
    
    if not phone_number:
        return jsonify({'success': False, 'message': 'Phone number is required'}), 400
        
    try:
        # Clear any existing verification
        if 'phone_verification' in session:
            session.pop('phone_verification')
            
        result = start_phone_verification(phone_number)
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone_number = data.get('phone_number')
    code = data.get('code')
    
    if not phone_number or not code:
        return jsonify({'success': False, 'message': 'Phone number and verification code are required'}), 400
        
    try:
        result = verify_phone_otp(phone_number, code)
        if result.get('success'):
            return jsonify(result)
        return jsonify(result), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/user', methods=['GET'])
@auth_required
def get_user():
    user = session.get('user', {})
    return jsonify({
        'phone_number': user.get('phone_number'),
        'auth_time': user.get('auth_time')
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@auth_bp.route('/test-protected', methods=['GET'])
@auth_required
def test_protected():
    user = session.get('user', {})
    return jsonify({
        'message': 'You have access to this protected route', 
        'phone_number': user.get('phone_number')
    }) 