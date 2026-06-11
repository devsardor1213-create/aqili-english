import sqlite3

def seed_grammar():
    conn = sqlite3.connect("bot_database.sqlite")
    cursor = conn.cursor()
    
    grammar_rules = [
        ("Present Simple (Oddiy Hozirgi Zamon)", "Ushbu zamon doimiy, takrorlanib turadigan ish-harakatlarni ifodalash uchun ishlatiladi.\n\n✅ Darak (Affirmative):\nI/You/We/They + V (fe'l)\nHe/She/It + V(s/es)\nMisol: I play tennis. She plays tennis.\n\n❌ Inkor (Negative):\nI/You/We/They + do not (don't) + V\nHe/She/It + does not (doesn't) + V\nMisol: I don't play. He doesn't play.\n\n❓ So'roq (Question):\nDo + I/You/We/They + V?\nDoes + He/She/It + V?\nMisol: Do you play? Does he play?"),
        ("Present Continuous (Hozirgi Davomiy Zamon)", "Ayni vaqtda davom etayotgan ish-harakatlar uchun ishlatiladi.\n\n✅ Darak: S + am/is/are + V(ing)\nMisol: I am reading a book now.\n\n❌ Inkor: S + am/is/are + not + V(ing)\nMisol: I am not reading a book.\n\n❓ So'roq: Am/Is/Are + S + V(ing)?\nMisol: Are you reading a book?"),
        ("Past Simple (Oddiy O'tgan Zamon)", "O'tgan vaqtda tugallangan harakatlar uchun ishlatiladi.\n\n✅ Darak: S + V(ed) (yoki noto'g'ri fe'lning 2-shakli)\nMisol: I played football yesterday. I went to school.\n\n❌ Inkor: S + did not (didn't) + V\nMisol: I didn't play. I didn't go.\n\n❓ So'roq: Did + S + V?\nMisol: Did you play? Did he go?"),
        ("Future Simple (Oddiy Kelasi Zamon)", "Kelajakdagi maqsad va harakatlar uchun ishlatiladi.\n\n✅ Darak: S + will + V\nMisol: I will go to Tashkent tomorrow.\n\n❌ Inkor: S + will not (won't) + V\nMisol: I won't go.\n\n❓ So'roq: Will + S + V?\nMisol: Will you go?"),
        ("Present Perfect (Hozirgi Tugallangan Zamon)", "O'tmishda boshlanib, hozirgina tugagan yoki natijasi hozir ham ko'rinib turgan ish-harakatlar.\n\n✅ Darak: S + have/has + V(3/ed)\nMisol: I have finished my homework.\n\n❌ Inkor: S + have/has + not + V(3/ed)\nMisol: I haven't finished.\n\n❓ So'roq: Have/Has + S + V(3/ed)?\nMisol: Have you finished?")
    ]
    
    # Just seed 5 basic ones for now
    cursor.execute("SELECT COUNT(*) FROM grammar")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.executemany("INSERT INTO grammar (title, content) VALUES (?, ?)", grammar_rules)
        conn.commit()
        print("Grammar seeded successfully.")
    else:
        print("Grammar already exists.")
        
    conn.close()

if __name__ == "__main__":
    seed_grammar()
