import sqlite3

def update_grammar():
    conn = sqlite3.connect("bot_database.sqlite")
    cursor = conn.cursor()
    
    grammar_rules = [
        ("Present Simple (Oddiy Hozirgi Zamon)", "Ushbu zamon doimiy, takrorlanib turadigan ish-harakatlarni ifodalash uchun ishlatiladi.\n\n✅ Darak (Affirmative):\nI/You/We/They + V (fe'l)\nHe/She/It + V(s/es)\nMisol: I play tennis. (Men tennis o'ynayman) She plays tennis. (U tennis o'ynaydi)\n\n❌ Inkor (Negative):\nI/You/We/They + do not (don't) + V\nHe/She/It + does not (doesn't) + V\nMisol: I don't play. (Men o'ynamayman) He doesn't play. (U o'ynamaydi)\n\n❓ So'roq (Question):\nDo + I/You/We/They + V?\nDoes + He/She/It + V?\nMisol: Do you play? (Siz o'ynaysizmi?) Does he play? (U o'ynaydimi?)"),
        
        ("Present Continuous (Hozirgi Davomiy Zamon)", "Ayni vaqtda davom etayotgan ish-harakatlar uchun ishlatiladi.\n\n✅ Darak: S + am/is/are + V(ing)\nMisol: I am reading a book now. (Men hozir kitob o'qiyapman)\n\n❌ Inkor: S + am/is/are + not + V(ing)\nMisol: I am not reading a book. (Men kitob o'qimayapman)\n\n❓ So'roq: Am/Is/Are + S + V(ing)?\nMisol: Are you reading a book? (Siz kitob o'qiyapsizmi?)"),
        
        ("Past Simple (Oddiy O'tgan Zamon)", "O'tgan vaqtda aniq tugallangan harakatlar uchun ishlatiladi.\n\n✅ Darak: S + V(ed) (yoki noto'g'ri fe'lning 2-shakli)\nMisol: I played football yesterday. (Men kecha futbol o'ynadim) I went to school. (Men maktabga bordim)\n\n❌ Inkor: S + did not (didn't) + V\nMisol: I didn't play. (Men o'ynamadim) I didn't go. (Men bormadim)\n\n❓ So'roq: Did + S + V?\nMisol: Did you play? (Siz o'ynadingizmi?) Did he go? (U bordimi?)"),
        
        ("Future Simple (Oddiy Kelasi Zamon)", "Kelajakdagi harakatlar va qarorlar uchun ishlatiladi.\n\n✅ Darak: S + will + V\nMisol: I will go to Tashkent tomorrow. (Men ertaga Toshkentga boraman)\n\n❌ Inkor: S + will not (won't) + V\nMisol: I won't go. (Men bormayman)\n\n❓ So'roq: Will + S + V?\nMisol: Will you go? (Siz borasizmi?)"),
        
        ("Present Perfect (Hozirgi Tugallangan Zamon)", "O'tmishda sodir bo'lgan, lekin natijasi hozir ham muhim bo'lgan ish-harakatlar.\n\n✅ Darak: S + have/has + V(3/ed)\nMisol: I have finished my homework. (Men uy vazifamni tugatib bo'ldim)\n\n❌ Inkor: S + have/has + not + V(3/ed)\nMisol: I haven't finished. (Men tugatganim yo'q)\n\n❓ So'roq: Have/Has + S + V(3/ed)?\nMisol: Have you finished? (Siz tugatib bo'ldingizmi?)")
    ]
    
    # Just update the existing ones by title
    for title, content in grammar_rules:
        cursor.execute("UPDATE grammar SET content = ? WHERE title = ?", (content, title))
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_grammar()
    print("Grammar translated")
