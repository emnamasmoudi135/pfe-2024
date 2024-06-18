# app/api/userManagement/decorators.py
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('sub', {}).get('role', 'user')
            print(f"Role in token: {user_role}")  # Add this line to debug
            if user_role != required_role:
                print(f"Unauthorized access. Required role: {required_role}, user role: {user_role}")
                return jsonify({"error": "Unauthorized"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
