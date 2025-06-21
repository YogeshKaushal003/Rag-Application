from flask import Blueprint, request, jsonify
from app import db
from app.models.models import User
from app.auth.utils import hash_password, check_password, generate_tokens
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "User already exists"}), 409

    user = User(
        email=data['email'],
        password_hash=hash_password(data['password'])
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password(data['password'], user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    tokens = generate_tokens(identity=user.id)
    return jsonify(tokens), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token}), 200
