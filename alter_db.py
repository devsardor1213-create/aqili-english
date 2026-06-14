import sqlite3

def upgrade():
    conn = sqlite3.connect("bot_database.sqlite")
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN target_lang TEXT DEFAULT 'en'")
        print("target_lang added to users")
    except Exception as e:
        print(e)
        
    try:
        cursor.execute("ALTER TABLE words ADD COLUMN lang TEXT DEFAULT 'en'")
        print("lang added to words")
    except Exception as e:
        print(e)
        
    try:
        cursor.execute("ALTER TABLE daily_words ADD COLUMN lang TEXT DEFAULT 'en'")
        print("lang added to daily_words")
    except Exception as e:
        print(e)
        
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_tests (
                telegram_id INTEGER,
                word_id INTEGER,
                UNIQUE(telegram_id, word_id)
            )
        """)
        print("user_tests created")
    except Exception as e:
        print(e)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    upgrade()
