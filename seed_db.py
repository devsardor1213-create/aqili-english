import sqlite3

words_data = {
    'en': [
        ('hello', 'salom'), ('world', 'dunyo'), ('apple', 'olma'), ('book', 'kitob'), ('water', 'suv'),
        ('house', 'uy'), ('car', 'mashina'), ('sun', 'quyosh'), ('moon', 'oy'), ('star', 'yulduz'),
        ('friend', 'do\'st'), ('family', 'oila'), ('tree', 'daraxt'), ('flower', 'gul'), ('sky', 'osmon'),
        ('dog', 'it'), ('cat', 'mushuk'), ('bird', 'qush'), ('fish', 'baliq'), ('bread', 'non'),
        ('milk', 'sut'), ('tea', 'choy'), ('coffee', 'qahva'), ('door', 'eshik'), ('window', 'deraza'),
        ('chair', 'stul'), ('table', 'stol'), ('pen', 'ruchka'), ('pencil', 'qalam'), ('paper', 'qog\'oz')
    ],
    'ru': [
        ('привет', 'salom'), ('мир', 'dunyo'), ('яблоко', 'olma'), ('книга', 'kitob'), ('вода', 'suv'),
        ('дом', 'uy'), ('машина', 'mashina'), ('солнце', 'quyosh'), ('луна', 'oy'), ('звезда', 'yulduz'),
        ('друг', 'do\'st'), ('семья', 'oila'), ('дерево', 'daraxt'), ('цветок', 'gul'), ('небо', 'osmon'),
        ('собака', 'it'), ('кошка', 'mushuk'), ('птица', 'qush'), ('рыба', 'baliq'), ('хлеб', 'non'),
        ('молоко', 'sut'), ('чай', 'choy'), ('кофе', 'qahva'), ('дверь', 'eshik'), ('окно', 'deraza'),
        ('стул', 'stul'), ('стол', 'stol'), ('ручка', 'ruchka'), ('карандаш', 'qalam'), ('бумага', 'qog\'oz')
    ],
    'kr': [
        ('안녕 (annyeong)', 'salom'), ('세상 (sesang)', 'dunyo'), ('사과 (sagwa)', 'olma'), ('책 (chaek)', 'kitob'), ('물 (mul)', 'suv'),
        ('집 (jip)', 'uy'), ('차 (cha)', 'mashina'), ('태양 (taeyang)', 'quyosh'), ('달 (dal)', 'oy'), ('별 (byeol)', 'yulduz'),
        ('친구 (chingu)', 'do\'st'), ('가족 (gajok)', 'oila'), ('나무 (namu)', 'daraxt'), ('꽃 (kkot)', 'gul'), ('하늘 (haneul)', 'osmon'),
        ('개 (gae)', 'it'), ('고양이 (goyangi)', 'mushuk'), ('새 (sae)', 'qush'), ('물고기 (mulgogi)', 'baliq'), ('빵 (ppang)', 'non'),
        ('우유 (uyu)', 'sut'), ('차 (cha)', 'choy'), ('커피 (keopi)', 'qahva'), ('문 (mun)', 'eshik'), ('창문 (changmun)', 'deraza'),
        ('의자 (uija)', 'stul'), ('탁자 (takja)', 'stol'), ('펜 (pen)', 'ruchka'), ('연필 (yeonpil)', 'qalam'), ('종이 (jongi)', 'qog\'oz')
    ],
    'tr': [
        ('merhaba', 'salom'), ('dünya', 'dunyo'), ('elma', 'olma'), ('kitap', 'kitob'), ('su', 'suv'),
        ('ev', 'uy'), ('araba', 'mashina'), ('güneş', 'quyosh'), ('ay', 'oy'), ('yıldız', 'yulduz'),
        ('arkadaş', 'do\'st'), ('aile', 'oila'), ('ağaç', 'daraxt'), ('çiçek', 'gul'), ('gökyüzü', 'osmon'),
        ('köpek', 'it'), ('kedi', 'mushuk'), ('kuş', 'qush'), ('balık', 'baliq'), ('ekmek', 'non'),
        ('süt', 'sut'), ('çay', 'choy'), ('kahve', 'qahva'), ('kapı', 'eshik'), ('pencere', 'deraza'),
        ('sandalye', 'stul'), ('masa', 'stol'), ('kalem', 'ruchka'), ('kurşun kalem', 'qalam'), ('kağıt', 'qog\'oz')
    ]
}

grammar_data = {
    'en': [
        ('Present Simple', 'Bu zamon odat tusiga kirgan, doimiy takrorlanuvchi harakatlarni ifodalaydi.\n\nDarak: I play chess.\nInkor: I do not play chess.\nSo\'roq: Do I play chess?'),
        ('Present Continuous', 'Bu zamon ayni paytda, gapirilayotgan vaqtda sodir bo\'layotgan harakatlarni ifodalaydi.\n\nDarak: I am playing chess.\nInkor: I am not playing chess.\nSo\'roq: Am I playing chess?'),
        ('Past Simple', 'Bu zamon o\'tgan zamonda tugallangan harakatlarni ifodalaydi.\n\nDarak: I played chess yesterday.\nInkor: I did not play chess yesterday.\nSo\'roq: Did I play chess yesterday?'),
        ('Future Simple', 'Bu zamon kelajakda sodir bo\'ladigan harakatlarni ifodalaydi.\n\nDarak: I will play chess.\nInkor: I will not play chess.\nSo\'roq: Will I play chess?')
    ],
    'ru': [
        ('Hастоящее время (Present)', 'Rus tilida hozirgi zamon (настоящее время) ayni paytda sodir bo\'layotgan yoki odatiy harakatlarni ifodalaydi.\n\nDarak: Я читаю (Men o\'qiyapman).\nInkor: Я не читаю.\nSo\'roq: Я читаю?'),
        ('Прошедшее время (Past)', 'O\'tgan zamon harakatning o\'tib ketganini bildiradi. U fe\'lga -л, -ла, -ло, -ли qo\'shimchalarini qo\'shish bilan yasaladi.\n\nDarak: Я читал (Men o\'qidim).\nInkor: Я не читал.\nSo\'roq: Ты читал?'),
        ('Будущее время (Future)', 'Kelasi zamon harakatning kelajakda sodir bo\'lishini bildiradi.\n\nDarak: Я буду читать (Men o\'qiyman).\nInkor: Я не буду читать.\nSo\'roq: Ты будешь читать?'),
        ('Предлоги (Predloglar)', 'Rus tilida joyni bildirish uchun В (ichida) va НА (ustida) predloglari ishlatiladi.\n\nВ школе (Maktabda).\nНа столе (Stol ustida).')
    ],
    'kr': [
        ('Hozirgi zamon (Present Tense)', 'Koreys tilida hozirgi zamonni yasash uchun fe\'l o\'zagiga -아/어요 (-a/eoyo) qo\'shiladi.\n\nDarak: 저는 가요 (Men boryapman/boraman).\nInkor: 저는 안 가요 (Men bormayapman).\nSo\'roq: 가요? (Boryapsizmi?)'),
        ('O\'tgan zamon (Past Tense)', 'O\'tgan zamon -았/었어요 (-ass/eosseoyo) qo\'shimchasi orqali yasaladi.\n\nDarak: 저는 갔어요 (Men bordim).\nInkor: 저는 안 갔어요 (Men bormadim).\nSo\'roq: 갔어요? (Bordingizmi?)'),
        ('Kelasi zamon (Future Tense)', 'Kelasi zamon -(으)ㄹ 거예요 (-[eu]l geoyeyo) orqali yasaladi.\n\nDarak: 저는 갈 거예요 (Men boraman).\nInkor: 저는 안 갈 거예요 (Men bormayman).\nSo\'roq: 갈 거예요? (Borasizmi?)'),
        ('Hurmat shakli (Polite form)', 'Koreys tilida o\'zidan kattalarga gapirganda fe\'lga -(으)시- (-[eu]si-) qo\'shiladi.\n\n가시다 (Bormoq - hurmat ma\'nosida).\n할아버지께서 가십니다 (Bobom boryaptilar).')
    ],
    'tr': [
        ('Şimdiki Zaman', 'Turk tilida hozirgi zamon (Şimdiki Zaman) -yor qo\'shimchasi orqali yasaladi.\n\nDarak: Ben geliyorum (Men kelyapman).\nInkor: Ben gelmiyorum.\nSo\'roq: Ben geliyor muyum?'),
        ('Geniş Zaman', 'Odatiy harakatlar uchun Geniş Zaman (-r, -ar, -er) ishlatiladi.\n\nDarak: Ben gelirim (Men kelaman).\nInkor: Ben gelmem.\nSo\'roq: Ben gelir miyim?'),
        ('Geçmiş Zaman (Bilinen)', 'O\'tgan zamon (-di, -dı, -du, -dü) qo\'shimchalari orqali yasaladi.\n\nDarak: Ben geldim (Men keldim).\nInkor: Ben gelmedim.\nSo\'roq: Ben geldim mi?'),
        ('Gelecek Zaman', 'Kelasi zamon (-ecek, -acak) qo\'shimchalari bilan yasaladi.\n\nDarak: Ben geleceğim (Men kelaman).\nInkor: Ben gelmeyeceğim.\nSo\'roq: Ben gelecek miyim?')
    ]
}

def seed_database():
    conn = sqlite3.connect("bot_database.sqlite")
    cursor = conn.cursor()
    
    # Check words
    for lang, words in words_data.items():
        cursor.execute("SELECT count(*) FROM words WHERE lang = ?", (lang,))
        if cursor.fetchone()[0] == 0:
            for word, translation in words:
                cursor.execute("INSERT INTO words (english_word, uzbek_translation, lang) VALUES (?, ?, ?)", (word, translation, lang))
            print(f"{lang.upper()} so'zlari qo'shildi ({len(words)} ta).")
            
    # Check grammar
    for lang, grammars in grammar_data.items():
        cursor.execute("SELECT count(*) FROM grammar WHERE lang = ?", (lang,))
        if cursor.fetchone()[0] == 0:
            for title, content in grammars:
                cursor.execute("INSERT INTO grammar (title, content, lang) VALUES (?, ?, ?)", (title, content, lang))
            print(f"{lang.upper()} grammatikasi qo'shildi ({len(grammars)} ta).")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_database()
    print("Barcha tillar uchun ma'lumotlar bazaga to'liq joylandi!")
