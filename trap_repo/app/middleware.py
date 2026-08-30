"""Auth middleware decorators for Flask routes."""

from functools import wraps

from flask import request, jsonify

from .auth import decode_token
from .user_models import UserStore


user_store = UserStore()


def token_required(f):
    """Decorator that requires a valid JWT token in the Authorization header."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        payload = decode_token(token)
        if payload is None:
            return jsonify({"error": "Invalid or expired token"}), 401

        user = user_store.get_by_id(payload["user_id"])
        if user is None:
            return jsonify({"error": "User not found"}), 401

        request.current_user = user
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """Decorator that requires admin role."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        payload = decode_token(token)
        if payload is None:
            return jsonify({"error": "Invalid or expired token"}), 401

        if payload.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403

        user = user_store.get_by_id(payload["user_id"])
        if user is None:
            return jsonify({"error": "User not found"}), 401

        request.current_user = user
        return f(*args, **kwargs)

    return decorated
