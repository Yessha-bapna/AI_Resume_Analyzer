from __init__ import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(100))
    experience_level = db.Column(db.String(50))
    employment_type = db.Column(db.String(50))  # Full-time, Part-time, etc.
    jd_pdf_path = db.Column(db.String(255))  # Path to uploaded JD PDF file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    creator = db.relationship('User', backref='created_jobs')
    resume_analyses = db.relationship('ResumeAnalysis', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'requirements': self.requirements,
            'location': self.location,
            'experience_level': self.experience_level,
            'employment_type': self.employment_type,
            'jd_pdf_path': self.jd_pdf_path,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'is_active': self.is_active,
            'application_count': len(self.resume_analyses)
        }

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # PDF, DOCX
    extracted_text = db.Column(db.Text)
    parsed_data = db.Column(db.Text)  # JSON string of structured data
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    analyses = db.relationship('ResumeAnalysis', backref='resume', lazy=True, cascade='all, delete-orphan')
    
    def set_parsed_data(self, data):
        self.parsed_data = json.dumps(data)
    
    def get_parsed_data(self):
        if self.parsed_data:
            return json.loads(self.parsed_data)
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'extracted_text': self.extracted_text[:500] + '...' if self.extracted_text and len(self.extracted_text) > 500 else self.extracted_text,
            'parsed_data': self.get_parsed_data(),
            'uploaded_at': self.uploaded_at.isoformat(),
            'user_id': self.user_id
        }

class ResumeAnalysis(db.Model):
    __tablename__ = 'resume_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'), nullable=False)
    
    # Analysis results
    relevance_score = db.Column(db.Float, default=0.0)
    verdict = db.Column(db.String(20), default='Low')  # High, Medium, Low
    missing_skills = db.Column(db.Text)  # JSON string
    missing_certifications = db.Column(db.Text)  # JSON string
    missing_projects = db.Column(db.Text)  # JSON string
    improvement_suggestions = db.Column(db.Text)
    
    # Ranking system
    rank = db.Column(db.Integer, default=0)
    is_in_queue = db.Column(db.Boolean, default=True)
    queue_position = db.Column(db.Integer, default=0)
    
    # Analysis metadata
    analysis_status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    analysis_started_at = db.Column(db.DateTime)
    analysis_completed_at = db.Column(db.DateTime)
    analysis_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_missing_skills(self, skills):
        self.missing_skills = json.dumps(skills) if skills else None
    
    def get_missing_skills(self):
        if self.missing_skills:
            return json.loads(self.missing_skills)
        return []
    
    def set_missing_certifications(self, certifications):
        self.missing_certifications = json.dumps(certifications) if certifications else None
    
    def get_missing_certifications(self):
        if self.missing_certifications:
            return json.loads(self.missing_certifications)
        return []
    
    def set_missing_projects(self, projects):
        self.missing_projects = json.dumps(projects) if projects else None
    
    def get_missing_projects(self):
        if self.missing_projects:
            return json.loads(self.missing_projects)
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'job_id': self.job_id,
            'relevance_score': self.relevance_score,
            'verdict': self.verdict,
            'missing_skills': self.get_missing_skills(),
            'missing_certifications': self.get_missing_certifications(),
            'missing_projects': self.get_missing_projects(),
            'improvement_suggestions': self.improvement_suggestions,
            'rank': self.rank,
            'is_in_queue': self.is_in_queue,
            'queue_position': self.queue_position,
            'analysis_status': self.analysis_status,
            'analysis_started_at': self.analysis_started_at.isoformat() if self.analysis_started_at else None,
            'analysis_completed_at': self.analysis_completed_at.isoformat() if self.analysis_completed_at else None,
            'analysis_notes': self.analysis_notes,
            'created_at': self.created_at.isoformat(),
            'resume': self.resume.to_dict() if self.resume else None,
            'user': self.resume.user.to_dict() if self.resume and self.resume.user else None
        }

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    application_status = db.Column(db.String(20), default='pending')  # pending, reviewed, shortlisted, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref='job_applications')
    job = db.relationship('JobDescription', backref='job_applications')
    resume = db.relationship('Resume', backref='job_applications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'resume_id': self.resume_id,
            'application_status': self.application_status,
            'applied_at': self.applied_at.isoformat(),
            'notes': self.notes,
            'resume': self.resume.to_dict() if self.resume else None,
            'job': self.job.to_dict() if self.job else None
        }

# Index for better query performance
db.Index('idx_resume_analysis_job_rank', ResumeAnalysis.job_id, ResumeAnalysis.rank)
db.Index('idx_resume_analysis_queue', ResumeAnalysis.job_id, ResumeAnalysis.queue_position)
db.Index('idx_applications_user_job', Application.user_id, Application.job_id)
