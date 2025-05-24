from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import CrimeRecord, Location, Profile
from app import db
import uuid
from datetime import datetime

crime_records_bp = Blueprint('crime_records', __name__)

@crime_records_bp.route('/', methods=['POST'])
@jwt_required()
def create_crime_record():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Create location first
    location = Location(
        city=data['location']['city'],
        latitude=data['location']['latitude'],
        longitude=data['location']['longitude'],
        police_station=data['location'].get('police_station'),
        district=data['location'].get('district')
    )
    
    try:
        db.session.add(location)
        db.session.flush()  # Get the location_id
        
        # Create crime record
        crime_record = CrimeRecord(
            id=str(uuid.uuid4()),
            title=data['title'],
            description=data.get('description'),
            crime_type=data['crime_type'],
            date_time=datetime.fromisoformat(data['date_time']),
            location_id=location.location_id,
            department_category=data.get('department_category'),
            progress=data.get('progress', 0),
            priority=data.get('priority', 'Medium'),
            status=data.get('status', 'open')
        )
        
        db.session.add(crime_record)
        db.session.commit()
        
        return jsonify({
            'message': 'Crime record created successfully',
            'crime_record': {
                'id': crime_record.id,
                'title': crime_record.title,
                'crime_type': crime_record.crime_type,
                'status': crime_record.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@crime_records_bp.route('/', methods=['GET'])
@jwt_required()
def get_crime_records():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    crime_type = request.args.get('crime_type')
    
    query = CrimeRecord.query
    
    if status:
        query = query.filter_by(status=status)
    if crime_type:
        query = query.filter_by(crime_type=crime_type)
    
    pagination = query.order_by(CrimeRecord.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    crime_records = [{
        'id': record.id,
        'title': record.title,
        'crime_type': record.crime_type,
        'date_time': record.date_time.isoformat(),
        'status': record.status,
        'priority': record.priority,
        'progress': record.progress
    } for record in pagination.items]
    
    return jsonify({
        'crime_records': crime_records,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@crime_records_bp.route('/<crime_id>', methods=['GET'])
@jwt_required()
def get_crime_record(crime_id):
    crime_record = CrimeRecord.query.get(crime_id)
    
    if not crime_record:
        return jsonify({'error': 'Crime record not found'}), 404
    
    location = Location.query.get(crime_record.location_id)
    
    return jsonify({
        'id': crime_record.id,
        'title': crime_record.title,
        'description': crime_record.description,
        'crime_type': crime_record.crime_type,
        'date_time': crime_record.date_time.isoformat(),
        'location': {
            'city': location.city,
            'latitude': float(location.latitude),
            'longitude': float(location.longitude),
            'police_station': location.police_station,
            'district': location.district
        },
        'department_category': crime_record.department_category,
        'progress': crime_record.progress,
        'priority': crime_record.priority,
        'status': crime_record.status,
        'created_at': crime_record.created_at.isoformat(),
        'updated_at': crime_record.updated_at.isoformat()
    }), 200

@crime_records_bp.route('/<crime_id>', methods=['PUT'])
@jwt_required()
def update_crime_record(crime_id):
    crime_record = CrimeRecord.query.get(crime_id)
    
    if not crime_record:
        return jsonify({'error': 'Crime record not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        crime_record.title = data['title']
    if 'description' in data:
        crime_record.description = data['description']
    if 'crime_type' in data:
        crime_record.crime_type = data['crime_type']
    if 'date_time' in data:
        crime_record.date_time = datetime.fromisoformat(data['date_time'])
    if 'department_category' in data:
        crime_record.department_category = data['department_category']
    if 'progress' in data:
        crime_record.progress = data['progress']
    if 'priority' in data:
        crime_record.priority = data['priority']
    if 'status' in data:
        crime_record.status = data['status']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Crime record updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@crime_records_bp.route('/<crime_id>', methods=['DELETE'])
@jwt_required()
def delete_crime_record(crime_id):
    crime_record = CrimeRecord.query.get(crime_id)
    
    if not crime_record:
        return jsonify({'error': 'Crime record not found'}), 404
    
    try:
        db.session.delete(crime_record)
        db.session.commit()
        return jsonify({'message': 'Crime record deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 