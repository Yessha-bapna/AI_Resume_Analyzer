from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from __init__ import db
from models import Application, JobDescription, Resume, User, ResumeAnalysis
from services.resume_parser import ResumeParser
from services.ai_analyzer import AIAnalyzer
from services.ranking_service import ranking_service
from services.jd_pdf_parser import JDPDFParser
from datetime import datetime
import threading

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/', methods=['POST'])
@jwt_required()
def apply_for_job():
    """Apply for a job with a specific resume"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        job_id = data.get('job_id')
        resume_id = data.get('resume_id')
        
        if not job_id or not resume_id:
            return jsonify({'error': 'Job ID and Resume ID are required'}), 400
        
        # Verify job exists
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Verify resume belongs to user
        resume = Resume.query.filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Check if user already applied for this job
        existing_application = Application.query.filter(
            Application.user_id == user_id,
            Application.job_id == job_id
        ).first()
        
        if existing_application:
            return jsonify({
                'error': 'You have already applied for this job',
                'application': existing_application.to_dict()
            }), 400
        
        # Create application
        application = Application(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id
        )
        
        db.session.add(application)
        db.session.commit()
        
        # Start analysis in background
        def analyze_application():
            from __init__ import create_app
            app = create_app()
            with app.app_context():
                try:
                    print(f"Starting analysis for resume {resume_id} and job {job_id}")
                    
                    # Get parsed resume data
                    parsed_data = resume.get_parsed_data()
                    if not parsed_data:
                        print("No parsed data found, re-parsing resume...")
                        # Re-parse if needed
                        parser = ResumeParser()
                        parsed_data = parser.parse_resume(resume.file_path, resume.file_type.lower())
                        resume.set_parsed_data(parsed_data)
                        db.session.commit()
                        print("Resume parsed successfully")
                    
                    # Perform AI analysis with combined job description
                    print("Starting AI analysis...")
                    ai_analyzer = AIAnalyzer()
                    combined_job_description = JDPDFParser.get_combined_job_description(job)
                    analysis_result = ai_analyzer.perform_comprehensive_analysis(
                        parsed_data, 
                        combined_job_description
                    )
                    print(f"AI analysis completed with score: {analysis_result.get('relevance_score', 'N/A')}")
                    
                    # Create or update resume analysis
                    analysis = ResumeAnalysis.query.filter(
                        ResumeAnalysis.resume_id == resume_id,
                        ResumeAnalysis.job_id == job_id
                    ).first()
                    
                    if not analysis:
                        analysis = ResumeAnalysis(
                            resume_id=resume_id,
                            job_id=job_id,
                            analysis_status='completed'
                        )
                        db.session.add(analysis)
                    
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
                    
                    # Add to ranking system
                    print("Adding to ranking system...")
                    try:
                        ranking_service.add_to_ranking(analysis)
                        print("Successfully added to ranking system")
                    except Exception as ranking_error:
                        print(f"Error adding to ranking system: {ranking_error}")
                        # Continue anyway, don't fail the entire analysis
                    
                    # Check if this should be promoted to top
                    try:
                        ranking_service.promote_high_score_resume(job_id, min_score=80.0)
                        print("Promotion check completed")
                    except Exception as promotion_error:
                        print(f"Error in promotion check: {promotion_error}")
                        # Continue anyway
                    
                    db.session.commit()
                    print(f"Analysis completed successfully for resume {resume_id}")
                    
                except Exception as e:
                    print(f"Error in background analysis: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # Mark analysis as failed
                    try:
                        analysis = ResumeAnalysis.query.filter(
                            ResumeAnalysis.resume_id == resume_id,
                            ResumeAnalysis.job_id == job_id
                        ).first()
                        if analysis:
                            analysis.analysis_status = 'failed'
                            analysis.analysis_notes = str(e)
                            db.session.commit()
                    except Exception as db_error:
                        print(f"Error updating failed analysis: {db_error}")
        
        # Start background analysis
        thread = threading.Thread(target=analyze_application)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_applications():
    """Get applications for the current user"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Application.query.filter(Application.user_id == user_id)
        
        if status:
            query = query.filter(Application.application_status == status)
        
        applications = query.order_by(Application.applied_at.desc())\
            .paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        
        return jsonify({
            'applications': [app.to_dict() for app in applications.items],
            'total': applications.total,
            'pages': applications.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/<int:application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    """Get specific application details"""
    try:
        user_id = int(get_jwt_identity())
        
        application = Application.query.filter(
            Application.id == application_id,
            Application.user_id == user_id
        ).first()
        
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        return jsonify({'application': application.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/<int:application_id>', methods=['DELETE'])
@jwt_required()
def withdraw_application(application_id):
    """Withdraw an application"""
    try:
        user_id = int(get_jwt_identity())
        
        application = Application.query.filter(
            Application.id == application_id,
            Application.user_id == user_id
        ).first()
        
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        if application.application_status != 'pending':
            return jsonify({'error': 'Cannot withdraw application that has been reviewed'}), 400
        
        db.session.delete(application)
        db.session.commit()
        
        return jsonify({'message': 'Application withdrawn successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/test-analysis/<int:resume_id>/<int:job_id>', methods=['POST'])
@jwt_required()
def test_analysis(resume_id, job_id):
    """Test endpoint to manually trigger analysis (for debugging)"""
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
        
        print(f"Starting synchronous analysis for resume {resume_id} and job {job_id}")
        
        # Get parsed resume data
        parsed_data = resume.get_parsed_data()
        if not parsed_data:
            print("No parsed data found, re-parsing resume...")
            parser = ResumeParser()
            parsed_data = parser.parse_resume(resume.file_path, resume.file_type.lower())
            resume.set_parsed_data(parsed_data)
            db.session.commit()
            print("Resume parsed successfully")
        
        # Perform AI analysis with combined job description
        print("Starting AI analysis...")
        ai_analyzer = AIAnalyzer()
        combined_job_description = JDPDFParser.get_combined_job_description(job)
        analysis_result = ai_analyzer.perform_comprehensive_analysis(
            parsed_data, 
            combined_job_description
        )
        print(f"AI analysis completed with score: {analysis_result.get('relevance_score', 'N/A')}")
        
        # Create or update resume analysis
        analysis = ResumeAnalysis.query.filter(
            ResumeAnalysis.resume_id == resume_id,
            ResumeAnalysis.job_id == job_id
        ).first()
        
        if not analysis:
            analysis = ResumeAnalysis(
                resume_id=resume_id,
                job_id=job_id,
                analysis_status='completed'
            )
            db.session.add(analysis)
        
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
        
        # Add to ranking system
        print("Adding to ranking system...")
        ranking_service.add_to_ranking(analysis)
        
        # Check if this should be promoted to top
        ranking_service.promote_high_score_resume(job_id, min_score=80.0)
        
        db.session.commit()
        print(f"Analysis completed successfully for resume {resume_id}")
        
        return jsonify({
            'message': 'Analysis completed successfully',
            'analysis': analysis.to_dict(),
            'analysis_result': analysis_result
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in test analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/process-pending', methods=['POST'])
@jwt_required()
def process_pending_applications():
    """Process all pending applications synchronously (for debugging)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Check if user is admin
        from models import User
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get all pending applications
        pending_applications = Application.query.filter_by(application_status='pending').all()
        
        if not pending_applications:
            return jsonify({'message': 'No pending applications found'}), 200
        
        processed_count = 0
        errors = []
        
        for application in pending_applications:
            try:
                print(f"Processing application {application.id}...")
                
                # Get resume and job
                resume = Resume.query.get(application.resume_id)
                job = JobDescription.query.get(application.job_id)
                
                if not resume or not job:
                    errors.append(f"Application {application.id}: Resume or job not found")
                    continue
                
                # Get parsed resume data
                parsed_data = resume.get_parsed_data()
                if not parsed_data:
                    print(f"Parsing resume {resume.id}...")
                    parser = ResumeParser()
                    parsed_data = parser.parse_resume(resume.file_path, resume.file_type.lower())
                    resume.set_parsed_data(parsed_data)
                    db.session.commit()
                
                # Perform AI analysis
                print(f"Starting AI analysis for application {application.id}...")
                ai_analyzer = AIAnalyzer()
                combined_job_description = JDPDFParser.get_combined_job_description(job)
                analysis_result = ai_analyzer.perform_comprehensive_analysis(
                    parsed_data, 
                    combined_job_description
                )
                print(f"AI analysis completed with score: {analysis_result.get('relevance_score', 'N/A')}")
                
                # Create or update resume analysis
                analysis = ResumeAnalysis.query.filter(
                    ResumeAnalysis.resume_id == application.resume_id,
                    ResumeAnalysis.job_id == application.job_id
                ).first()
                
                if not analysis:
                    analysis = ResumeAnalysis(
                        resume_id=application.resume_id,
                        job_id=application.job_id,
                        analysis_status='completed'
                    )
                    db.session.add(analysis)
                
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
                
                # Add to ranking system
                try:
                    ranking_service.add_to_ranking(analysis)
                    print(f"Successfully added application {application.id} to ranking system")
                except Exception as ranking_error:
                    print(f"Error adding application {application.id} to ranking system: {ranking_error}")
                    errors.append(f"Application {application.id}: Ranking error - {ranking_error}")
                
                # Check if this should be promoted to top
                try:
                    ranking_service.promote_high_score_resume(application.job_id, min_score=80.0)
                except Exception as promotion_error:
                    print(f"Error in promotion check for application {application.id}: {promotion_error}")
                
                processed_count += 1
                print(f"Application {application.id} processed successfully")
                
            except Exception as e:
                error_msg = f"Application {application.id}: {str(e)}"
                errors.append(error_msg)
                print(f"Error processing application {application.id}: {e}")
                import traceback
                traceback.print_exc()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Processed {processed_count} applications',
            'errors': errors,
            'total_pending': len(pending_applications)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
