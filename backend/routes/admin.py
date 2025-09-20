from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from __init__ import db
from models import JobDescription, ResumeAnalysis, User
from services.ranking_service import ranking_service

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def admin_dashboard():
    try:
        # Get basic statistics
        total_jobs = JobDescription.query.filter(JobDescription.is_active == True).count()
        total_resumes = ResumeAnalysis.query.count()
        completed_analyses = ResumeAnalysis.query.filter(
            ResumeAnalysis.analysis_status == 'completed'
        ).count()
        pending_analyses = ResumeAnalysis.query.filter(
            ResumeAnalysis.analysis_status == 'pending'
        ).count()
        
        # Get recent jobs
        recent_jobs = JobDescription.query\
            .filter(JobDescription.is_active == True)\
            .order_by(JobDescription.created_at.desc())\
            .limit(5)\
            .all()
        
        return jsonify({
            'stats': {
                'total_jobs': total_jobs,
                'total_resumes': total_resumes,
                'completed_analyses': completed_analyses,
                'pending_analyses': pending_analyses
            },
            'recent_jobs': [job.to_dict() for job in recent_jobs]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/jobs/<int:job_id>/rankings', methods=['GET'])
@jwt_required()
@admin_required
def get_job_rankings(job_id):
    try:
        # Verify job exists
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get rankings
        limit = request.args.get('limit', 50, type=int)
        rankings = ranking_service.get_job_rankings(job_id, limit)
        
        # Get queue status
        queue_status = ranking_service.get_queue_status(job_id)
        
        return jsonify({
            'job': job.to_dict(),
            'rankings': rankings,
            'queue_status': queue_status
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/jobs/<int:job_id>/queue-status', methods=['GET'])
@jwt_required()
@admin_required
def get_queue_status(job_id):
    try:
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        queue_status = ranking_service.get_queue_status(job_id)
        
        return jsonify({
            'job_id': job_id,
            'queue_status': queue_status
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analyses', methods=['GET'])
@jwt_required()
@admin_required
def get_all_analyses():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        job_id = request.args.get('job_id', type=int)
        status = request.args.get('status', '')
        verdict = request.args.get('verdict', '')
        
        # Build query
        query = ResumeAnalysis.query
        
        if job_id:
            query = query.filter(ResumeAnalysis.job_id == job_id)
        
        if status:
            query = query.filter(ResumeAnalysis.analysis_status == status)
        
        if verdict:
            query = query.filter(ResumeAnalysis.verdict == verdict)
        
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

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.order_by(User.created_at.desc())\
            .paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_user_admin(user_id):
    try:
        # Don't allow modifying own admin status
        current_user_id = get_jwt_identity()
        if user_id == current_user_id:
            return jsonify({'error': 'Cannot modify your own admin status'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_admin = not user.is_admin
        db.session.commit()
        
        return jsonify({
            'message': f'User admin status updated to {user.is_admin}',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analyses/<int:analysis_id>/reprocess', methods=['POST'])
@jwt_required()
@admin_required
def reprocess_analysis(analysis_id):
    try:
        analysis = ResumeAnalysis.query.get(analysis_id)
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Reset analysis status
        analysis.analysis_status = 'pending'
        analysis.analysis_started_at = None
        analysis.analysis_completed_at = None
        analysis.analysis_notes = None
        
        # Add back to queue
        ranking_service.add_to_queue(analysis_id, analysis.job_id)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Analysis queued for reprocessing',
            'analysis_id': analysis_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_system_stats():
    try:
        # Get various statistics
        stats = {
            'users': {
                'total': User.query.count(),
                'admins': User.query.filter(User.is_admin == True).count(),
                'regular_users': User.query.filter(User.is_admin == False).count()
            },
            'jobs': {
                'total': JobDescription.query.count(),
                'active': JobDescription.query.filter(JobDescription.is_active == True).count(),
                'inactive': JobDescription.query.filter(JobDescription.is_active == False).count()
            },
            'analyses': {
                'total': ResumeAnalysis.query.count(),
                'completed': ResumeAnalysis.query.filter(ResumeAnalysis.analysis_status == 'completed').count(),
                'pending': ResumeAnalysis.query.filter(ResumeAnalysis.analysis_status == 'pending').count(),
                'processing': ResumeAnalysis.query.filter(ResumeAnalysis.analysis_status == 'processing').count(),
                'failed': ResumeAnalysis.query.filter(ResumeAnalysis.analysis_status == 'failed').count()
            },
            'verdicts': {
                'high': ResumeAnalysis.query.filter(ResumeAnalysis.verdict == 'High').count(),
                'medium': ResumeAnalysis.query.filter(ResumeAnalysis.verdict == 'Medium').count(),
                'low': ResumeAnalysis.query.filter(ResumeAnalysis.verdict == 'Low').count()
            }
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/debug/system-status', methods=['GET'])
@jwt_required()
@admin_required
def get_system_status():
    """Debug endpoint to check system status"""
    try:
        from models import User, JobDescription, Resume, ResumeAnalysis, Application
        
        # Get counts
        user_count = User.query.count()
        job_count = JobDescription.query.count()
        resume_count = Resume.query.count()
        analysis_count = ResumeAnalysis.query.count()
        application_count = Application.query.count()
        
        # Get recent analyses
        recent_analyses = ResumeAnalysis.query.order_by(ResumeAnalysis.created_at.desc()).limit(5).all()
        
        # Get recent applications
        recent_applications = Application.query.order_by(Application.applied_at.desc()).limit(5).all()
        
        return jsonify({
            'counts': {
                'users': user_count,
                'jobs': job_count,
                'resumes': resume_count,
                'analyses': analysis_count,
                'applications': application_count
            },
            'recent_analyses': [analysis.to_dict() for analysis in recent_analyses],
            'recent_applications': [app.to_dict() for app in recent_applications]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
