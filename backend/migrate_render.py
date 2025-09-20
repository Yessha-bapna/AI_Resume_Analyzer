#!/usr/bin/env python3
"""
Render production database migration script
"""
import os
import hashlib
from __init__ import create_app, db
from models import User, JobDescription, Resume, ResumeAnalysis, Application

def migrate_render():
    app = create_app()
    with app.app_context():
        try:
            print("🚀 Starting Render production database migration...")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create admin user if not exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                # Hash the password 'admin123'
                password_hash = hashlib.pbkdf2_hmac('sha256', b'admin123', b'salt', 100000).hex()
                
                admin = User(
                    username='admin',
                    email='admin@resumeanalyzer.com',
                    password_hash=password_hash,
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created (username: admin, password: admin123)")
            else:
                print("✅ Admin user already exists")
            
            # Check if we have any data
            user_count = User.query.count()
            job_count = JobDescription.query.count()
            resume_count = Resume.query.count()
            
            print(f"📊 Database Status:")
            print(f"   - Users: {user_count}")
            print(f"   - Jobs: {job_count}")
            print(f"   - Resumes: {resume_count}")
            
            print("🎉 Render production migration completed successfully!")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

if __name__ == '__main__':
    success = migrate_render()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        exit(1)
