#db_schema.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from main import app, db

def print_schema():
    with app.app_context():
        result = db.engine.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
        for row in result:
            print(f"Table name: {row['name']}")
            print(f"Schema: {row['sql']}\n")

if __name__ == "__main__":
    print_schema()