#!/usr/bin/env python3
"""
Reset database script - drops and recreates all tables
"""

import os
from __init__ import create_app, db

def reset_database():
    """Drop and recreate all database tables"""
    print("🔄 Resetting database...")
    
    app = create_app()
    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            print("✅ All tables dropped")
            
            # Create all tables
            db.create_all()
            print("✅ All tables created")
            
            print("🎉 Database reset completed successfully!")
            
        except Exception as e:
            print(f"❌ Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
