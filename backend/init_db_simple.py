#!/usr/bin/env python3
"""
Simple database initialization script for Resume Analyzer
Creates database and default admin user
"""

import os
import sys
from __init__ import create_app, db
from models import User

def create_default_admin():
    """Create default admin user"""
    admin_username = "admin"
    admin_email = "admin@example.com"
    admin_password = "admin123"
    
    # Check if admin already exists
    existing_admin = User.query.filter_by(username=admin_username).first()
    if existing_admin:
        print(f"Admin user '{admin_username}' already exists")
        return True
    
    # Create admin user
    admin = User(
        username=admin_username,
        email=admin_email,
        is_admin=True
    )
    admin.set_password(admin_password)
    
    try:
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{admin_username}' created successfully")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("⚠️  Please change the password after first login!")
        return True
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.session.rollback()
        return False

def main():
    """Main initialization function"""
    print("Resume Analyzer Database Initialization")
    print("=" * 40)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully")
            
            # Create admin user
            print("\nCreating admin user...")
            if create_default_admin():
                print("\n✅ Database initialization completed successfully!")
                print("\nYou can now:")
                print("1. Start the Flask server: python app.py")
                print("2. Start the React frontend: cd frontend && npm run dev")
                print("3. Login with admin credentials")
            else:
                print("Database initialization completed with errors")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error during initialization: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
