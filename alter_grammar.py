import sqlite3

def upgrade():
    conn = sqlite3.connect("bot_database.sqlite")
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE grammar ADD COLUMN lang TEXT DEFAULT 'en'")
        print("lang added to grammar")
    except Exception as e:
        print(e)
        
    try:
        cursor.execute("DROP TABLE IF EXISTS user_grammar")
        cursor.execute("""
            CREATE TABLE user_grammar (
                user_id INTEGER,
                lang TEXT,
                current_grammar_id INTEGER DEFAULT 1,
                last_date TEXT,
                UNIQUE(user_id, lang)
            )
        """)
        print("user_grammar recreated with lang support")
    except Exception as e:
        print(e)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    upgrade()
