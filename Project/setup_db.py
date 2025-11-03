#!/usr/bin/env python3
# generated with gpt
"""
Database setup script for Course Compass messaging feature.
Run this script to create the Message table in the database.
"""

from app import create_app
from app.models import db

def setup_database():
    """Create all database tables including the new Message table."""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        print("\nThe following tables are now available:")
        print("  - user")
        print("  - user_requirements")
        print("  - review")
        print("  - message (NEW!)")
        print("\nYou can now run the application with: python run.py")

if __name__ == "__main__":
    setup_database()
