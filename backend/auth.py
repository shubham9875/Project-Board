from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import jwt

def create_access_token(sub: str, minutes: int):
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

def decode_token(token: str):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"detail": "Not authenticated"}), 401
        token = auth.split(" ", 1)[1].strip()
        try:
            payload = decode_token(token)
            request.user_id = int(payload.get("sub"))
        except Exception as e:
            return jsonify({"detail": "Invalid token"}), 401
        return f(*args, **kwargs)
    return wrapper
