# db_init.py

from main import app, db, initUsers

# Ensure the app context is available
with app.app_context():
    # Create all tables
    db.create_all()
    # Initialize the Users table
    initUsers()
    print("Database initialized!")
