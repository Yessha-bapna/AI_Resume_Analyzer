from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from __init__ import db
from models import JobDescription, User
import os
import uuid
from werkzeug.utils import secure_filename

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/', methods=['GET'])
@jwt_required()
def get_jobs():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        is_active = request.args.get('is_active', True, type=lambda x: x.lower() == 'true')
        
        # Build query
        query = JobDescription.query
        
        if search:
            query = query.filter(
                db.or_(
                    JobDescription.title.contains(search),
                    JobDescription.company.contains(search),
                    JobDescription.description.contains(search)
                )
            )
        
        if is_active is not None:
            query = query.filter(JobDescription.is_active == is_active)
        
        # Order by creation date (newest first)
        query = query.order_by(JobDescription.created_at.desc())
        
        # Paginate
        jobs = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs.items],
            'total': jobs.total,
            'pages': jobs.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job(job_id):
    try:
        job = JobDescription.query.get(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({'job': job.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/', methods=['POST'])
@jwt_required()
def create_job():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        # Check if user is admin
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Check if request has form data (multipart/form-data)
        if request.form:
            data = request.form
        else:
            data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('description'):
            return jsonify({'error': 'Title and description are required'}), 400
        
        # Handle PDF upload
        jd_pdf_path = None
        if 'jd_pdf' in request.files:
            file = request.files['jd_pdf']
            if file and file.filename != '':
                # Validate file type
                if not file.filename.lower().endswith('.pdf'):
                    return jsonify({'error': 'Only PDF files are allowed'}), 400
                
                # Generate unique filename
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                
                # Create job descriptions upload directory
                jd_upload_dir = os.path.join('uploads', 'job_descriptions')
                os.makedirs(jd_upload_dir, exist_ok=True)
                
                # Save file
                file_path = os.path.join(jd_upload_dir, unique_filename)
                file.save(file_path)
                jd_pdf_path = file_path
        
        # Create new job
        job = JobDescription(
            title=data['title'],
            company=data.get('company', ''),
            description=data['description'],
            requirements=data.get('requirements', ''),
            location=data.get('location', ''),
            experience_level=data.get('experience_level', ''),
            employment_type=data.get('employment_type', ''),
            jd_pdf_path=jd_pdf_path,
            created_by=user_id
        )
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify({
            'message': 'Job created successfully',
            'job': job.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        # Check if user is admin
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        job = JobDescription.query.get(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            job.title = data['title']
        if 'company' in data:
            job.company = data['company']
        if 'description' in data:
            job.description = data['description']
        if 'requirements' in data:
            job.requirements = data['requirements']
        if 'location' in data:
            job.location = data['location']
        if 'experience_level' in data:
            job.experience_level = data['experience_level']
        if 'employment_type' in data:
            job.employment_type = data['employment_type']
        if 'is_active' in data:
            job.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Job updated successfully',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        # Check if user is admin
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        job = JobDescription.query.get(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Soft delete by setting is_active to False
        job.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Job deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
