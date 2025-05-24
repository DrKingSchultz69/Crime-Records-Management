from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Report, Profile
from app import db
import uuid

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/', methods=['POST'])
@jwt_required()
def create_report():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    report = Report(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        title=data['title'],
        report_type=data['report_type'],
        content=data.get('content'),
        findings=data.get('findings'),
        recommendations=data.get('recommendations')
    )
    
    try:
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Report created successfully',
            'report': {
                'id': report.id,
                'title': report.title,
                'report_type': report.report_type
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/', methods=['GET'])
@jwt_required()
def get_reports():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    report_type = request.args.get('report_type')
    
    query = Report.query
    
    if report_type:
        query = query.filter_by(report_type=report_type)
    
    pagination = query.order_by(Report.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    reports = []
    for report in pagination.items:
        author = Profile.query.get(report.user_id)
        reports.append({
            'id': report.id,
            'title': report.title,
            'report_type': report.report_type,
            'author': author.name if author else None,
            'created_at': report.created_at.isoformat()
        })
    
    return jsonify({
        'reports': reports,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@reports_bp.route('/<report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    report = Report.query.get(report_id)
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    author = Profile.query.get(report.user_id)
    
    return jsonify({
        'id': report.id,
        'title': report.title,
        'report_type': report.report_type,
        'content': report.content,
        'findings': report.findings,
        'recommendations': report.recommendations,
        'author': {
            'id': author.id,
            'name': author.name,
            'badge_number': author.badge_number
        } if author else None,
        'created_at': report.created_at.isoformat()
    }), 200

@reports_bp.route('/<report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    report = Report.query.get(report_id)
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        report.title = data['title']
    if 'report_type' in data:
        report.report_type = data['report_type']
    if 'content' in data:
        report.content = data['content']
    if 'findings' in data:
        report.findings = data['findings']
    if 'recommendations' in data:
        report.recommendations = data['recommendations']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Report updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/<report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    report = Report.query.get(report_id)
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    try:
        db.session.delete(report)
        db.session.commit()
        return jsonify({'message': 'Report deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 