
import sqlite3

# Connect to sqlite db 
conn = sqlite3.connect('new_development.db')
cursor = conn.cursor()

# 'users' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    _name TEXT,
    _uid TEXT,
    _password TEXT,
    _role TEXT,
    _pfp TEXT,
    kasm_server_needed BOOLEAN,
    status INTEGER
)
''')

#  'sections' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    _name TEXT,
    _abbreviation TEXT
)
''')

# 'user_sections' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_sections (
    user_id INTEGER,
    section_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(section_id) REFERENCES sections(id)
)
''')

conn.commit()
conn.close()
