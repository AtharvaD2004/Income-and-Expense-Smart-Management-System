import jwt, functools
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(p):   return generate_password_hash(p, method="pbkdf2:sha256")
def verify_password(p, h): return check_password_hash(h, p)

def generate_token(user_id):
    payload = {"user_id": user_id, "exp": datetime.utcnow() + timedelta(days=7), "iat": datetime.utcnow()}
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth  = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth.split(" ")[1]
        if not token:
            return jsonify({"error": "Token missing."}), 401
        try:
            payload = decode_token(token)
            user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired. Please log in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token."}), 401
        from models.database import User
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found."}), 401
        return f(user, *args, **kwargs)
    return decorated
