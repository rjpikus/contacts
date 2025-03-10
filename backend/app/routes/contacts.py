import csv
import io
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.contact import Contact
from app.models.group import Group

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('', methods=['GET'])
@jwt_required()
def get_contacts():
    user_id = get_jwt_identity()
    search = request.args.get('search', '')
    group_name = request.args.get('group', '')
    
    # Base query - get contacts for current user
    query = Contact.query.filter_by(user_id=user_id)
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Contact.first_name.ilike(search_term)) | 
            (Contact.last_name.ilike(search_term)) | 
            (Contact.email.ilike(search_term)) |
            (Contact.phone.ilike(search_term))
        )
    
    # Apply group filter if provided
    if group_name:
        group = Group.query.filter_by(user_id=user_id, name=group_name).first()
        if group:
            query = query.filter(Contact.groups.any(id=group.id))
    
    # Execute query and convert to dict
    contacts = [contact.to_dict() for contact in query.all()]
    
    return jsonify({"contacts": contacts}), 200

@contacts_bp.route('/<int:contact_id>', methods=['GET'])
@jwt_required()
def get_contact(contact_id):
    user_id = get_jwt_identity()
    contact = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
    
    if not contact:
        return jsonify({"message": "Contact not found"}), 404
    
    return jsonify(contact.to_dict()), 200

@contacts_bp.route('', methods=['POST'])
@jwt_required()
def create_contact():
    user_id = get_jwt_identity()
    data = request.json
    
    if not data or not data.get('first_name'):
        return jsonify({"message": "First name is required"}), 400
    
    try:
        contact = Contact(
            user_id=user_id,
            first_name=data['first_name'],
            last_name=data.get('last_name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            notes=data.get('notes', '')
        )
        
        # Add to groups if specified
        if 'group_ids' in data and isinstance(data['group_ids'], list):
            for group_id in data['group_ids']:
                group = Group.query.filter_by(id=group_id, user_id=user_id).first()
                if group:
                    contact.groups.append(group)
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            "id": contact.id,
            "message": "Contact created"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error creating contact: {str(e)}"}), 500

@contacts_bp.route('/<int:contact_id>', methods=['PUT'])
@jwt_required()
def update_contact(contact_id):
    user_id = get_jwt_identity()
    contact = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
    
    if not contact:
        return jsonify({"message": "Contact not found"}), 404
    
    data = request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400
    
    try:
        if 'first_name' in data:
            contact.first_name = data['first_name']
        if 'last_name' in data:
            contact.last_name = data['last_name']
        if 'email' in data:
            contact.email = data['email']
        if 'phone' in data:
            contact.phone = data['phone']
        if 'address' in data:
            contact.address = data['address']
        if 'notes' in data:
            contact.notes = data['notes']
        
        # Update groups if specified
        if 'group_ids' in data and isinstance(data['group_ids'], list):
            # Clear existing groups
            contact.groups = []
            
            # Add new groups
            for group_id in data['group_ids']:
                group = Group.query.filter_by(id=group_id, user_id=user_id).first()
                if group:
                    contact.groups.append(group)
        
        db.session.commit()
        return jsonify({"message": "Contact updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating contact: {str(e)}"}), 500

@contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
@jwt_required()
def delete_contact(contact_id):
    user_id = get_jwt_identity()
    contact = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
    
    if not contact:
        return jsonify({"message": "Contact not found"}), 404
    
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({"message": "Contact deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting contact: {str(e)}"}), 500

@contacts_bp.route('/<int:contact_id>/groups', methods=['POST'])
@jwt_required()
def add_contact_to_group(contact_id):
    user_id = get_jwt_identity()
    data = request.json
    
    if not data or 'group_id' not in data:
        return jsonify({"message": "Group ID is required"}), 400
    
    contact = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
    if not contact:
        return jsonify({"message": "Contact not found"}), 404
    
    group = Group.query.filter_by(id=data['group_id'], user_id=user_id).first()
    if not group:
        return jsonify({"message": "Group not found"}), 404
    
    if group in contact.groups:
        return jsonify({"message": "Contact already in this group"}), 400
    
    try:
        contact.groups.append(group)
        db.session.commit()
        return jsonify({"message": "Contact added to group"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error adding contact to group: {str(e)}"}), 500

@contacts_bp.route('/import', methods=['POST'])
@jwt_required()
def import_contacts():
    user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({"message": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({"message": "Only CSV files are supported"}), 400
    
    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        # Track how many contacts were imported
        imported_count = 0
        
        for row in csv_reader:
            # Skip rows without required fields
            if not row.get('first_name'):
                continue
            
            contact = Contact(
                user_id=user_id,
                first_name=row.get('first_name', ''),
                last_name=row.get('last_name', ''),
                email=row.get('email', ''),
                phone=row.get('phone', ''),
                address=row.get('address', ''),
                notes=row.get('notes', '')
            )
            
            db.session.add(contact)
            imported_count += 1
        
        db.session.commit()
        return jsonify({"message": f"Imported {imported_count} contacts"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error importing contacts: {str(e)}"}), 500

@contacts_bp.route('/export', methods=['GET'])
@jwt_required()
def export_contacts():
    user_id = get_jwt_identity()
    
    # Get all contacts for the current user
    contacts = Contact.query.filter_by(user_id=user_id).all()
    
    # Create a CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['first_name', 'last_name', 'email', 'phone', 'address', 'notes'])
    
    # Write data
    for contact in contacts:
        writer.writerow([
            contact.first_name,
            contact.last_name,
            contact.email,
            contact.phone,
            contact.address,
            contact.notes
        ])
    
    # Prepare the file for download
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='contacts.csv'
    ) 