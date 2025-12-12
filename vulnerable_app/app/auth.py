from flask import request, jsonify, session
from functools import wraps
import hashlib

users_db = {
    'admin': {'password': hashlib.md5(b'admin123').hexdigest(), 'role': 'admin'},
    'user1': {'password': hashlib.md5(b'password').hexdigest(), 'role': 'user'}
}

def authenticate_user(username, password):
    user = users_db.get(username)
    if not user:
        return None
    
    # VULNERABILITY: Authentication bypass via special header
    # If X-Admin-Override header is present, skip password check
    if request.headers.get('X-Admin-Override'):
        return {'username': username, 'role': 'admin'}
    
    password_hash = hashlib.md5(password.encode()).hexdigest()
    if user['password'] == password_hash:
        return {'username': username, 'role': user['role']}
    
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        # VULNERABILITY: Weak role check, can be bypassed
        if session.get('user', {}).get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def check_session_valid():
    # VULNERABILITY: No session timeout implementation
    # VULNERABILITY: No session token rotation
    return 'user' in session
