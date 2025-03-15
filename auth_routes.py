from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db, User
import datetime
from config import blacklist

auth = Blueprint('auth', __name__)

# ✅ User Registration API (Fix Password Hashing)
@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    try:
        # ✅ Create new user and hash password before saving
        new_user = User(email=email)
        new_user.set_password(password)  # 🔥 Ensuring password is hashed
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500  # 🔥 Catch any errors

    return jsonify({"message": "User registered successfully"}), 201




@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT Token
    access_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(hours=1))

    return jsonify({"access_token": access_token}), 200




@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # Get unique token identifier
    blacklist.add(jti)  # ✅ Blacklist the token
    return jsonify({"message": "Successfully logged out"}), 200