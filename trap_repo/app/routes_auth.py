"""Authentication and user management routes."""

from flask import Blueprint, jsonify, request

from .auth import create_token
from .middleware import token_required, admin_required, user_store

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    required = ["username", "email", "password"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    if user_store.get_by_username(data["username"]):
        return jsonify({"error": "Username already taken"}), 409

    user = user_store.create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"],
    )
    token = create_token(user.id, user.role)
    return jsonify({"user": user.to_dict(), "token": token}), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password required"}), 400

    user = user_store.verify_password(data["username"], data["password"])
    if user is None:
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_token(user.id, user.role)
    return jsonify({"user": user.to_dict(), "token": token})


@auth_bp.route("/auth/profile", methods=["GET"])
@token_required
def profile():
    return jsonify({"user": request.current_user.to_dict()})


@auth_bp.route("/auth/users", methods=["GET"])
@admin_required
def list_users():
    return jsonify({"users": user_store.list_all(), "count": user_store.count()})
