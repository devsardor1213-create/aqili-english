import sqlite3

def seed_words():
    conn = sqlite3.connect("bot_database.sqlite")
    cursor = conn.cursor()
    
    words = [
        ("Hello", "Salom"),
        ("Goodbye", "Xayr"),
        ("Thank you", "Rahmat"),
        ("Please", "Iltimos"),
        ("Yes", "Ha"),
        ("No", "Yo'q"),
        ("Good", "Yaxshi"),
        ("Bad", "Yomon"),
        ("Big", "Katta"),
        ("Small", "Kichik"),
        ("Water", "Suv"),
        ("Food", "Ovqat"),
        ("House", "Uy"),
        ("Friend", "Do'st"),
        ("Family", "Oila"),
        ("Time", "Vaqt"),
        ("Day", "Kun"),
        ("Night", "Tun"),
        ("Morning", "Ertalab"),
        ("Evening", "Kechqurun"),
        ("Boy", "O'g'il bola"),
        ("Girl", "Qiz bola"),
        ("Man", "Erkak"),
        ("Woman", "Ayol"),
        ("Sun", "Quyosh"),
        ("Moon", "Oy"),
        ("Star", "Yulduz"),
        ("Sky", "Osmon"),
        ("Earth", "Yer"),
        ("Fire", "Olov"),
        ("Book", "Kitob"),
        ("Pen", "Ruchka"),
        ("School", "Maktab"),
        ("Student", "O'quvchi"),
        ("Teacher", "O'qituvchi"),
        ("Work", "Ish"),
        ("Money", "Pul"),
        ("Car", "Moshina"),
        ("Road", "Yo'l"),
        ("City", "Shahar"),
        ("Country", "Davlat"),
        ("World", "Dunyo"),
        ("Love", "Sevgi"),
        ("Happy", "Xursand"),
        ("Sad", "Xafa"),
        ("Beautiful", "Chiroyli"),
        ("Ugly", "Xunuk"),
        ("Fast", "Tez"),
        ("Slow", "Sekin"),
        ("Always", "Har doim"),
        ("Never", "Hech qachon")
    ]
    
    # Check if words exist
    cursor.execute("SELECT COUNT(*) FROM words")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.executemany("INSERT INTO words (english_word, uzbek_translation) VALUES (?, ?)", words)
        conn.commit()
        print("Words seeded successfully.")
    else:
        print("Words already exist.")
        
    conn.close()

if __name__ == "__main__":
    seed_words()
