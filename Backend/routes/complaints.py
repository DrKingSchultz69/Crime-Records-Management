from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Complaint, Profile
from app import db
import uuid
from datetime import datetime

complaints_bp = Blueprint('complaints', __name__)

@complaints_bp.route('/', methods=['POST'])
@jwt_required()
def create_complaint():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Generate reference number (you might want to make this more sophisticated)
    reference_number = f"COMP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    complaint = Complaint(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        complainant_name=data['complainant_name'],
        complainant_contact=data['complainant_contact'],
        complaint_type=data['complaint_type'],
        description=data['description'],
        location=data['location'],
        reference_number=reference_number
    )
    
    try:
        db.session.add(complaint)
        db.session.commit()
        
        return jsonify({
            'message': 'Complaint submitted successfully',
            'complaint': {
                'id': complaint.id,
                'reference_number': complaint.reference_number,
                'status': complaint.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@complaints_bp.route('/', methods=['GET'])
@jwt_required()
def get_complaints():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    complaint_type = request.args.get('complaint_type')
    
    query = Complaint.query
    
    if status:
        query = query.filter_by(status=status)
    if complaint_type:
        query = query.filter_by(complaint_type=complaint_type)
    
    pagination = query.order_by(Complaint.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    complaints = [{
        'id': complaint.id,
        'reference_number': complaint.reference_number,
        'complainant_name': complaint.complainant_name,
        'complaint_type': complaint.complaint_type,
        'status': complaint.status,
        'progress': complaint.progress,
        'created_at': complaint.created_at.isoformat()
    } for complaint in pagination.items]
    
    return jsonify({
        'complaints': complaints,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@complaints_bp.route('/<complaint_id>', methods=['GET'])
@jwt_required()
def get_complaint(complaint_id):
    complaint = Complaint.query.get(complaint_id)
    
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404
    
    assigned_officer = None
    if complaint.assigned_to:
        officer = Profile.query.get(complaint.assigned_to)
        if officer:
            assigned_officer = {
                'id': officer.id,
                'name': officer.name,
                'badge_number': officer.badge_number
            }
    
    return jsonify({
        'id': complaint.id,
        'reference_number': complaint.reference_number,
        'complainant_name': complaint.complainant_name,
        'complainant_contact': complaint.complainant_contact,
        'complaint_type': complaint.complaint_type,
        'description': complaint.description,
        'location': complaint.location,
        'status': complaint.status,
        'progress': complaint.progress,
        'assigned_officer': assigned_officer,
        'created_at': complaint.created_at.isoformat(),
        'updated_at': complaint.updated_at.isoformat()
    }), 200

@complaints_bp.route('/<complaint_id>', methods=['PUT'])
@jwt_required()
def update_complaint(complaint_id):
    complaint = Complaint.query.get(complaint_id)
    
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404
    
    data = request.get_json()
    
    if 'status' in data:
        complaint.status = data['status']
    if 'progress' in data:
        complaint.progress = data['progress']
    if 'assigned_to' in data:
        complaint.assigned_to = data['assigned_to']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Complaint updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@complaints_bp.route('/<complaint_id>', methods=['DELETE'])
@jwt_required()
def delete_complaint(complaint_id):
    complaint = Complaint.query.get(complaint_id)
    
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404
    
    try:
        db.session.delete(complaint)
        db.session.commit()
        return jsonify({'message': 'Complaint deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 