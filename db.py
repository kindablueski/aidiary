import sqlite3

DATABASE = 'diary.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Create users table if it doesn't exist.
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            current_wellness INTEGER DEFAULT 100,
            quiz_taken INTEGER DEFAULT 0
        )
    ''')
    # Create entries table with analysis and tags columns.
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT,
            wellness_score INTEGER,
            tags TEXT,
            analysis TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
