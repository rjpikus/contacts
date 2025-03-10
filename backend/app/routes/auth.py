from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt_identity
)

from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password required"}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 400
    
    try:
        user = User(email=data['email'], password=data['password'])
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "User registered",
            "user_id": user.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error creating user: {str(e)}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password required"}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200 