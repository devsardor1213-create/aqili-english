import sqlite3
from datetime import date

DB_NAME = "bot_database.sqlite"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            first_name TEXT,
            username TEXT,
            xp INTEGER DEFAULT 0,
            last_activity TEXT,
            joined_date TEXT,
            is_blocked INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            last_bonus_date TEXT,
            target_lang TEXT DEFAULT 'en'
        )
    """)
    
    # Words table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english_word TEXT,
            uzbek_translation TEXT,
            lang TEXT DEFAULT 'en'
        )
    """)
    
    # Tests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_option TEXT
        )
    """)
    
    # Channels table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_username TEXT UNIQUE,
            channel_name TEXT
        )
    """)
    
    # Daily Words tracking (global)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_words (
            date TEXT,
            word_id INTEGER,
            lang TEXT DEFAULT 'en'
        )
    """)
    
    # User Tests Tracking (to prevent repeating tests)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_tests (
            telegram_id INTEGER,
            word_id INTEGER,
            UNIQUE(telegram_id, word_id)
        )
    """)
    
    # Grammar table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grammar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            voice_file_id TEXT
        )
    """)
    
    # User Grammar Progress
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_grammar (
            user_id INTEGER PRIMARY KEY,
            current_grammar_id INTEGER DEFAULT 1,
            last_date TEXT
        )
    """)
    
    # User state tracking (for inputs)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_states (
            telegram_id INTEGER PRIMARY KEY,
            state TEXT,
            data TEXT
        )
    """)

    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
