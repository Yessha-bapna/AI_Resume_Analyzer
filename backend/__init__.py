from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    
    # Load environment-specific configuration
    config_name = os.getenv('FLASK_ENV', 'development')
    from config import config
    app.config.from_object(config[config_name])

    # ✅ Define allowed origins
    allowed_origins = [
        "http://localhost:3000",  # Dev
        "https://ai-resume-analyzer-five-lake.vercel.app"  # Vercel Production,
        "https://ai-resume-analyzer-yesshas-projects.vercel.app"
    ]
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True
    )
    limiter.init_app(app)
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Import models after db is initialized
    from models import User, JobDescription, Resume, ResumeAnalysis, Application
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.jobs import jobs_bp
    from routes.resumes import resumes_bp
    from routes.admin import admin_bp
    from routes.applications import applications_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(resumes_bp, url_prefix='/api/resumes')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
