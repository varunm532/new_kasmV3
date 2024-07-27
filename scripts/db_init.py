import sqlite3
import os

def get_schema(db_path, tables):
    """Get the schema for the specified tables from the SQLite database."""
    schema = []
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        placeholders = ','.join('?' for table in tables)
        cursor.execute(f"SELECT name, sql FROM sqlite_master WHERE type='table' AND name IN ({placeholders});", tables)
        schema = cursor.fetchall()
    return schema

def print_schema(schema):
    """Print the schema."""
    for table_name, table_sql in schema:
        print(f"Table name: {table_name}")
        print(f"Schema: {table_sql}\n")

def build_new_db(new_db_path, schema):
    """Build a new SQLite database using the provided schema."""
    with sqlite3.connect(new_db_path) as conn:
        cursor = conn.cursor()
        for table_name, table_sql in schema:
            cursor.execute(table_sql)
        conn.commit()

# Paths to the old and new databases
old_db_path = 'instance/volumes/sqlite.db'
new_db_path = 'instance/volumes/sqlite_v2.db'
    
    # List of tables to transfer
tables_to_transfer = ['users', 'user_sections', 'sections']
    
    # Create the directory if it doesn't exist
os.makedirs(os.path.dirname(new_db_path), exist_ok=True)
    
    # Get the schema from the old database for the specified tables
schema = get_schema(old_db_path, tables_to_transfer)
    
    # Print the schema
print_schema(schema)
    
    # Build the new database with the extracted schema
build_new_db(new_db_path, schema)

print(f"New database created successfully at {new_db_path}.")
