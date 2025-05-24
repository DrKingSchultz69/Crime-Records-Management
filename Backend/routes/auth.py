from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Profile, UserRole
from app import db
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user = User(
        id=str(uuid.uuid4()),
        email=data['email'],
        password=generate_password_hash(data['password']),
        raw_user_meta_data={'name': data.get('name', data['email'])}
    )
    
    # Create profile
    profile = Profile(
        id=user.id,
        name=data.get('name', data['email']),
        email=data['email']
    )
    
    # Create user role
    user_role = UserRole(
        id=str(uuid.uuid4()),
        user_id=user.id,
        role='user'
    )
    
    try:
        db.session.add(user)
        db.session.add(profile)
        db.session.add(user_role)
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    profile = Profile.query.get(current_user_id)
    
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    return jsonify({
        'id': profile.id,
        'name': profile.name,
        'email': profile.email,
        'department': profile.department,
        'badge_number': profile.badge_number
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    profile = Profile.query.get(current_user_id)
    
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        profile.name = data['name']
    if 'department' in data:
        profile.department = data['department']
    if 'badge_number' in data:
        profile.badge_number = data['badge_number']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
