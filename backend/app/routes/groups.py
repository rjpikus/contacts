from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.group import Group

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('', methods=['GET'])
@jwt_required()
def get_groups():
    user_id = get_jwt_identity()
    groups = Group.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "groups": [group.to_dict() for group in groups]
    }), 200

@groups_bp.route('/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    user_id = get_jwt_identity()
    group = Group.query.filter_by(id=group_id, user_id=user_id).first()
    
    if not group:
        return jsonify({"message": "Group not found"}), 404
    
    return jsonify(group.to_dict()), 200

@groups_bp.route('', methods=['POST'])
@jwt_required()
def create_group():
    user_id = get_jwt_identity()
    data = request.json
    
    if not data or not data.get('name'):
        return jsonify({"message": "Group name is required"}), 400
    
    # Check if a group with the same name already exists
    existing_group = Group.query.filter_by(user_id=user_id, name=data['name']).first()
    if existing_group:
        return jsonify({"message": "A group with this name already exists"}), 400
    
    try:
        group = Group(user_id=user_id, name=data['name'])
        db.session.add(group)
        db.session.commit()
        
        return jsonify({
            "id": group.id,
            "message": "Group created"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error creating group: {str(e)}"}), 500

@groups_bp.route('/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_group(group_id):
    user_id = get_jwt_identity()
    data = request.json
    
    if not data or not data.get('name'):
        return jsonify({"message": "Group name is required"}), 400
    
    group = Group.query.filter_by(id=group_id, user_id=user_id).first()
    if not group:
        return jsonify({"message": "Group not found"}), 404
    
    # Check if another group with the same name already exists
    existing_group = Group.query.filter_by(user_id=user_id, name=data['name']).first()
    if existing_group and existing_group.id != group_id:
        return jsonify({"message": "A group with this name already exists"}), 400
    
    try:
        group.name = data['name']
        db.session.commit()
        
        return jsonify({"message": "Group updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating group: {str(e)}"}), 500

@groups_bp.route('/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    user_id = get_jwt_identity()
    group = Group.query.filter_by(id=group_id, user_id=user_id).first()
    
    if not group:
        return jsonify({"message": "Group not found"}), 404
    
    try:
        db.session.delete(group)
        db.session.commit()
        
        return jsonify({"message": "Group deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting group: {str(e)}"}), 500 