from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Location
from app import db

locations_bp = Blueprint('locations', __name__)

@locations_bp.route('/', methods=['POST'])
@jwt_required()
def create_location():
    data = request.get_json()
    
    location = Location(
        city=data['city'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        police_station=data.get('police_station'),
        district=data.get('district')
    )
    
    try:
        db.session.add(location)
        db.session.commit()
        
        return jsonify({
            'message': 'Location created successfully',
            'location': {
                'location_id': location.location_id,
                'city': location.city,
                'district': location.district
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@locations_bp.route('/', methods=['GET'])
@jwt_required()
def get_locations():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    city = request.args.get('city')
    district = request.args.get('district')
    
    query = Location.query
    
    if city:
        query = query.filter_by(city=city)
    if district:
        query = query.filter_by(district=district)
    
    pagination = query.order_by(Location.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    locations = [{
        'location_id': location.location_id,
        'city': location.city,
        'latitude': float(location.latitude),
        'longitude': float(location.longitude),
        'police_station': location.police_station,
        'district': location.district,
        'created_at': location.created_at.isoformat()
    } for location in pagination.items]
    
    return jsonify({
        'locations': locations,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@locations_bp.route('/<location_id>', methods=['GET'])
@jwt_required()
def get_location(location_id):
    location = Location.query.get(location_id)
    
    if not location:
        return jsonify({'error': 'Location not found'}), 404
    
    return jsonify({
        'location_id': location.location_id,
        'city': location.city,
        'latitude': float(location.latitude),
        'longitude': float(location.longitude),
        'police_station': location.police_station,
        'district': location.district,
        'created_at': location.created_at.isoformat()
    }), 200

@locations_bp.route('/<location_id>', methods=['PUT'])
@jwt_required()
def update_location(location_id):
    location = Location.query.get(location_id)
    
    if not location:
        return jsonify({'error': 'Location not found'}), 404
    
    data = request.get_json()
    
    if 'city' in data:
        location.city = data['city']
    if 'latitude' in data:
        location.latitude = data['latitude']
    if 'longitude' in data:
        location.longitude = data['longitude']
    if 'police_station' in data:
        location.police_station = data['police_station']
    if 'district' in data:
        location.district = data['district']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Location updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@locations_bp.route('/<location_id>', methods=['DELETE'])
@jwt_required()
def delete_location(location_id):
    location = Location.query.get(location_id)
    
    if not location:
        return jsonify({'error': 'Location not found'}), 404
    
    try:
        db.session.delete(location)
        db.session.commit()
        return jsonify({'message': 'Location deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 