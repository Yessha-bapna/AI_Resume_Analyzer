import os

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
    JWT_ACCESS_TOKEN_EXPIRES = False
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_NAME = 'access_token_cookie'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'

class DevelopmentConfig(Config):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///resume_analyzer.db')
    JWT_COOKIE_SECURE = False
    FLASK_DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    # Debug database URL
    _db_url = os.getenv('DATABASE_URL')
    print(f"DEBUG: DATABASE_URL = {_db_url}")
    
    if _db_url and _db_url.startswith('postgres://'):
        # Convert postgres:// to postgresql:// for newer versions
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
        print(f"DEBUG: Converted DATABASE_URL to: {_db_url}")
    
    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///resume_analyzer.db'
    print(f"DEBUG: Final SQLALCHEMY_DATABASE_URI = {SQLALCHEMY_DATABASE_URI}")
    
    JWT_COOKIE_SECURE = True
    FLASK_DEBUG = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
