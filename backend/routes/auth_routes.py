from flask import Blueprint, request, jsonify
from models.database import db, User
from utils.auth_utils import hash_password, verify_password, generate_token, login_required
from utils.validators import validate_register, validate_login

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data: return jsonify({"error": "JSON required."}), 400
    ok, err = validate_register(data)
    if not ok: return jsonify({"error": err}), 400
    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 409
    user = User(name=data["name"].strip(), email=email, password=hash_password(data["password"]))
    db.session.add(user); db.session.commit()
    return jsonify({"message": "Account created.", "token": generate_token(user.id), "user": user.to_dict()}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data: return jsonify({"error": "JSON required."}), 400
    ok, err = validate_login(data)
    if not ok: return jsonify({"error": err}), 400
    user = User.query.filter_by(email=data["email"].strip().lower()).first()
    if not user or not verify_password(data["password"], user.password):
        return jsonify({"error": "Invalid email or password."}), 401
    return jsonify({"message": "Login successful.", "token": generate_token(user.id), "user": user.to_dict()}), 200

@auth_bp.route("/profile", methods=["GET"])
@login_required
def profile(current_user):
    return jsonify({"user": current_user.to_dict()}), 200

@auth_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile(current_user):
    data = request.get_json() or {}
    if "name" in data:
        if len(data["name"].strip()) < 2: return jsonify({"error": "Name too short."}), 400
        current_user.name = data["name"].strip()
    if "new_password" in data:
        if not verify_password(data.get("current_password", ""), current_user.password):
            return jsonify({"error": "Current password is incorrect."}), 401
        if len(data["new_password"]) < 6: return jsonify({"error": "New password min 6 chars."}), 400
        current_user.password = hash_password(data["new_password"])
    db.session.commit()
    return jsonify({"message": "Profile updated.", "user": current_user.to_dict()}), 200
