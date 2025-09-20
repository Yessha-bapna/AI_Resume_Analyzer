from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from __init__ import db, limiter
from models import Resume, ResumeAnalysis, JobDescription, User
from services.resume_parser import ResumeParser
from services.ai_analyzer import AIAnalyzer
from services.ranking_service import ranking_service
from services.jd_pdf_parser import JDPDFParser

resumes_bp = Blueprint('resumes', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@resumes_bp.route('/upload', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def upload_resume():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF and DOCX files are allowed'}), 400
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Save file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Parse resume
        parser = ResumeParser()
        parsed_data = parser.parse_resume(file_path, file_extension)
        
        # Create resume record
        resume = Resume(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_type=file_extension.upper(),
            extracted_text=parsed_data['cleaned_text'],
            user_id=user_id
        )
        resume.set_parsed_data(parsed_data)
        
        db.session.add(resume)
        db.session.commit()
        
        return jsonify({
            'message': 'Resume uploaded and parsed successfully',
            'resume': resume.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Clean up uploaded file if parsing failed
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        return jsonify({'error': str(e)}), 500

@resumes_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_resumes():
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        resumes = Resume.query\
            .filter(Resume.user_id == user_id)\
            .order_by(Resume.uploaded_at.desc())\
            .paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        
        return jsonify({
            'resumes': [resume.to_dict() for resume in resumes.items],
            'total': resumes.total,
            'pages': resumes.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resumes_bp.route('/<int:resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    try:
        user_id = int(get_jwt_identity())
        resume = Resume.query.filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        return jsonify({'resume': resume.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resumes_bp.route('/analyze/<int:resume_id>/<int:job_id>', methods=['POST'])
@jwt_required()
def analyze_resume(resume_id, job_id):
    try:
        user_id = int(get_jwt_identity())
        
        # Verify resume belongs to user
        resume = Resume.query.filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Verify job exists
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Check if analysis already exists
        existing_analysis = ResumeAnalysis.query.filter(
            ResumeAnalysis.resume_id == resume_id,
            ResumeAnalysis.job_id == job_id
        ).first()
        
        if existing_analysis:
            return jsonify({
                'message': 'Analysis already exists',
                'analysis': existing_analysis.to_dict()
            }), 200
        
        # Create new analysis record
        analysis = ResumeAnalysis(
            resume_id=resume_id,
            job_id=job_id,
            analysis_status='pending'
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Add to queue
        queue_position = ranking_service.add_to_queue(analysis.id, job_id)
        
        # Start analysis in background (simplified version)
        try:
            # Get parsed resume data
            parsed_data = resume.get_parsed_data()
            if not parsed_data:
                # Re-parse if needed
                parser = ResumeParser()
                parsed_data = parser.parse_resume(resume.file_path, resume.file_type.lower())
                resume.set_parsed_data(parsed_data)
                db.session.commit()
            
            # Perform AI analysis with combined job description (including PDF)
            ai_analyzer = AIAnalyzer()
            combined_job_description = JDPDFParser.get_combined_job_description(job)
            analysis_result = ai_analyzer.perform_comprehensive_analysis(
                parsed_data, 
                combined_job_description
            )
            
            # Update analysis with results
            analysis.relevance_score = analysis_result['relevance_score']
            analysis.verdict = analysis_result['verdict']
            analysis.set_missing_skills(analysis_result.get('missing_skills', []))
            analysis.set_missing_certifications(analysis_result.get('missing_certifications', []))
            analysis.set_missing_projects(analysis_result.get('missing_projects', []))
            analysis.improvement_suggestions = '\n'.join(analysis_result.get('improvement_suggestions', []))
            analysis.analysis_status = 'completed'
            analysis.analysis_completed_at = datetime.utcnow()
            analysis.is_in_queue = False
            
            # Update rankings
            ranking_service.update_ranking(job_id, analysis)
            
            # Check if this should be promoted to top
            ranking_service.promote_high_score_resume(job_id, min_score=80.0)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Analysis completed successfully',
                'analysis': analysis.to_dict(),
                'queue_position': queue_position
            }), 200
            
        except Exception as analysis_error:
            # Mark analysis as failed
            analysis.analysis_status = 'failed'
            analysis.analysis_notes = str(analysis_error)
            db.session.commit()
            
            return jsonify({
                'message': 'Analysis queued but failed during processing',
                'error': str(analysis_error),
                'queue_position': queue_position
            }), 202
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@resumes_bp.route('/analyses', methods=['GET'])
@jwt_required()
def get_user_analyses():
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        job_id = request.args.get('job_id', type=int)
        
        query = ResumeAnalysis.query.join(Resume)\
            .filter(Resume.user_id == user_id)
        
        if job_id:
            query = query.filter(ResumeAnalysis.job_id == job_id)
        
        analyses = query.order_by(ResumeAnalysis.created_at.desc())\
            .paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        
        return jsonify({
            'analyses': [analysis.to_dict() for analysis in analyses.items],
            'total': analyses.total,
            'pages': analyses.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resumes_bp.route('/<int:resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id):
    try:
        user_id = int(get_jwt_identity())
        resume = Resume.query.filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Delete file from filesystem
        try:
            if os.path.exists(resume.file_path):
                os.remove(resume.file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
        
        # Delete from database (cascade will handle analyses)
        db.session.delete(resume)
        db.session.commit()
        
        return jsonify({'message': 'Resume deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
