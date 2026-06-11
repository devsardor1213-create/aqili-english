import sqlite3

def upgrade():
    conn = sqlite3.connect("bot_database.sqlite")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_bonus_date TEXT")
        conn.commit()
        print("last_bonus_date column added")
    except Exception as e:
        print(f"Error (maybe already exists): {e}")
    conn.close()

if __name__ == '__main__':
    upgrade()
