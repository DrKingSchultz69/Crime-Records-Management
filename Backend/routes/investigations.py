from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Investigation, CrimeRecord, Profile
from app import db
from datetime import datetime

investigations_bp = Blueprint('investigations', __name__)

@investigations_bp.route('/', methods=['POST'])
@jwt_required()
def create_investigation():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Check if crime record exists
    crime_record = CrimeRecord.query.get(data['crime_id'])
    if not crime_record:
        return jsonify({'error': 'Crime record not found'}), 404
    
    # Check if officer exists
    officer = Profile.query.get(current_user_id)
    if not officer:
        return jsonify({'error': 'Officer profile not found'}), 404
    
    investigation = Investigation(
        officer_id=current_user_id,
        crime_id=data['crime_id'],
        status=data.get('status', 'In Progress'),
        progress_notes=data.get('progress_notes'),
        assigned_department=data.get('assigned_department')
    )
    
    try:
        db.session.add(investigation)
        db.session.commit()
        
        return jsonify({
            'message': 'Investigation created successfully',
            'investigation': {
                'investigation_id': investigation.investigation_id,
                'crime_id': investigation.crime_id,
                'status': investigation.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@investigations_bp.route('/', methods=['GET'])
@jwt_required()
def get_investigations():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    crime_id = request.args.get('crime_id')
    
    query = Investigation.query
    
    if status:
        query = query.filter_by(status=status)
    if crime_id:
        query = query.filter_by(crime_id=crime_id)
    
    pagination = query.order_by(Investigation.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    investigations = []
    for investigation in pagination.items:
        officer = Profile.query.get(investigation.officer_id)
        crime = CrimeRecord.query.get(investigation.crime_id)
        
        investigations.append({
            'investigation_id': investigation.investigation_id,
            'crime_id': investigation.crime_id,
            'crime_title': crime.title if crime else None,
            'officer_name': officer.name if officer else None,
            'status': investigation.status,
            'assigned_department': investigation.assigned_department,
            'created_at': investigation.created_at.isoformat()
        })
    
    return jsonify({
        'investigations': investigations,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@investigations_bp.route('/<investigation_id>', methods=['GET'])
@jwt_required()
def get_investigation(investigation_id):
    investigation = Investigation.query.get(investigation_id)
    
    if not investigation:
        return jsonify({'error': 'Investigation not found'}), 404
    
    officer = Profile.query.get(investigation.officer_id)
    crime = CrimeRecord.query.get(investigation.crime_id)
    
    return jsonify({
        'investigation_id': investigation.investigation_id,
        'crime': {
            'id': crime.id,
            'title': crime.title,
            'crime_type': crime.crime_type,
            'status': crime.status
        } if crime else None,
        'officer': {
            'id': officer.id,
            'name': officer.name,
            'badge_number': officer.badge_number
        } if officer else None,
        'status': investigation.status,
        'progress_notes': investigation.progress_notes,
        'assigned_department': investigation.assigned_department,
        'created_at': investigation.created_at.isoformat(),
        'updated_at': investigation.updated_at.isoformat()
    }), 200

@investigations_bp.route('/<investigation_id>', methods=['PUT'])
@jwt_required()
def update_investigation(investigation_id):
    investigation = Investigation.query.get(investigation_id)
    
    if not investigation:
        return jsonify({'error': 'Investigation not found'}), 404
    
    data = request.get_json()
    
    if 'status' in data:
        investigation.status = data['status']
    if 'progress_notes' in data:
        investigation.progress_notes = data['progress_notes']
    if 'assigned_department' in data:
        investigation.assigned_department = data['assigned_department']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Investigation updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@investigations_bp.route('/<investigation_id>', methods=['DELETE'])
@jwt_required()
def delete_investigation(investigation_id):
    investigation = Investigation.query.get(investigation_id)
    
    if not investigation:
        return jsonify({'error': 'Investigation not found'}), 404
    
    try:
        db.session.delete(investigation)
        db.session.commit()
        return jsonify({'message': 'Investigation deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 