#!/usr/bin/env python3

""" db_init.py
Generates the database schema for all db models
- Initializes Users, Sections, and UserSections tables.

Usage: Run from the terminal as such:

Goto the scripts directory:
> cd scriipts; ./db_init.py

Or run from the root of the project:
> scripts/db_init.py
"""
import sys
import os

# Add the directory containing main.py to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the app and db objects
from __init__ import dbURI
from main import app, db, initUsers

# Obtain the app context 
with app.app_context():
    try:
        # Check if the database has any tables
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if tables:
            print("Warning, you are about to lose all data in the database!")
            print("Do you want to continue? (y/n)")
            response = input()
            if response.lower() != 'y':
                print("Exiting without making changes.")
                sys.exit(0)
        
        # Drop all tables defined in the project
        db.drop_all()
        print("All tables dropped.")
        
        # Create all tables
        db.create_all()
        print("All tables created.")
        
        # Initialize the Users table
        initUsers()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    
    # Log success 
    print("Database initialized!")