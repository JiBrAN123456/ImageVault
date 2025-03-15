from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

protected = Blueprint('protected', __name__)

# ✅ Protected Route (Only Authenticated Users Can Access)
@protected.route('/dashboard', methods=['GET'])
@jwt_required()  # 🔥 Requires JWT token
def dashboard():
    user_id = get_jwt_identity()
    return jsonify({"message": "Welcome to your dashboard!", "user_id": user_id}), 200
