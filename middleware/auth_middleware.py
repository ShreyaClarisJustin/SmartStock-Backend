from functools import wraps
from flask import request, jsonify, current_app
import jwt

def authenticate_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Access denied"}), 401

        try:
            token = token.replace("Bearer ", "")
            decoded = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            request.user = decoded
        except Exception as e:
            return jsonify({"error": "Invalid token"}), 400

        return f(*args, **kwargs)
    return decorated

def verify_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.user.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated

def is_employee(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.user.get("role") not in ["admin", "employee"]:
            return jsonify({"error": "Access denied"}), 403
        return f(*args, **kwargs)
    return decorated
