from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import PoliceStation
from app import db

police_stations_bp = Blueprint('police_stations', __name__)

@police_stations_bp.route('/', methods=['POST'])
@jwt_required()
def create_police_station():
    data = request.get_json()
    
    police_station = PoliceStation(
        name=data['name'],
        address=data['address'],
        district=data['district'],
        contact_number=data['contact_number'],
        officer_in_charge=data['officer_in_charge'],
        jurisdiction=data['jurisdiction'],
        department_categories=data['department_categories']
    )
    
    try:
        db.session.add(police_station)
        db.session.commit()
        
        return jsonify({
            'message': 'Police station created successfully',
            'police_station': {
                'station_id': police_station.station_id,
                'name': police_station.name,
                'district': police_station.district
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@police_stations_bp.route('/', methods=['GET'])
@jwt_required()
def get_police_stations():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    district = request.args.get('district')
    
    query = PoliceStation.query
    
    if district:
        query = query.filter_by(district=district)
    
    pagination = query.order_by(PoliceStation.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    police_stations = [{
        'station_id': station.station_id,
        'name': station.name,
        'address': station.address,
        'district': station.district,
        'contact_number': station.contact_number,
        'officer_in_charge': station.officer_in_charge,
        'jurisdiction': station.jurisdiction,
        'department_categories': station.department_categories,
        'created_at': station.created_at.isoformat()
    } for station in pagination.items]
    
    return jsonify({
        'police_stations': police_stations,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@police_stations_bp.route('/<station_id>', methods=['GET'])
@jwt_required()
def get_police_station(station_id):
    police_station = PoliceStation.query.get(station_id)
    
    if not police_station:
        return jsonify({'error': 'Police station not found'}), 404
    
    return jsonify({
        'station_id': police_station.station_id,
        'name': police_station.name,
        'address': police_station.address,
        'district': police_station.district,
        'contact_number': police_station.contact_number,
        'officer_in_charge': police_station.officer_in_charge,
        'jurisdiction': police_station.jurisdiction,
        'department_categories': police_station.department_categories,
        'created_at': police_station.created_at.isoformat()
    }), 200

@police_stations_bp.route('/<station_id>', methods=['PUT'])
@jwt_required()
def update_police_station(station_id):
    police_station = PoliceStation.query.get(station_id)
    
    if not police_station:
        return jsonify({'error': 'Police station not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        police_station.name = data['name']
    if 'address' in data:
        police_station.address = data['address']
    if 'district' in data:
        police_station.district = data['district']
    if 'contact_number' in data:
        police_station.contact_number = data['contact_number']
    if 'officer_in_charge' in data:
        police_station.officer_in_charge = data['officer_in_charge']
    if 'jurisdiction' in data:
        police_station.jurisdiction = data['jurisdiction']
    if 'department_categories' in data:
        police_station.department_categories = data['department_categories']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Police station updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@police_stations_bp.route('/<station_id>', methods=['DELETE'])
@jwt_required()
def delete_police_station(station_id):
    police_station = PoliceStation.query.get(station_id)
    
    if not police_station:
        return jsonify({'error': 'Police station not found'}), 404
    
    try:
        db.session.delete(police_station)
        db.session.commit()
        return jsonify({'message': 'Police station deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 