import telebot
from telebot import types
import sqlite3
import datetime
import time
import schedule
import threading
import os
import random
from gtts import gTTS

import config
import database

bot = telebot.TeleBot(config.BOT_TOKEN, num_threads=20)

# Initialize database
database.init_db()

def get_conn():
    return sqlite3.connect(database.DB_NAME, check_same_thread=False)

def check_subscription(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT channel_username FROM channels")
    channels = cursor.fetchall()
    conn.close()
    
    not_joined = []
    for (ch,) in channels:
        try:
            status = bot.get_chat_member(f"@{ch}", user_id).status
            if status not in ['member', 'administrator', 'creator']:
                not_joined.append(ch)
        except Exception as e:
            # If bot is not admin or channel doesn't exist, assume not joined to force fix
            not_joined.append(ch)
            print(f"Error checking sub for {ch}: {e}")
    return not_joined

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📖 So'zlar", "📝 Test ishlash")
    markup.row("📚 Grammatika", "📊 Statistikam")
    markup.row("🎁 Bonus", "🏆 Reyting")
    return markup

def admin_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📢 Xabar tarqatish", "📊 Foydalanuvchilar")
    markup.row("➕ Kanal qo'shish", "➖ Kanal o'chirish")
    markup.row("➕ So'z qo'shish", "➕ Grammatika qo'shish")
    markup.row("⬅️ Asosiy menyu")
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username or ""
    
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, is_admin FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute("INSERT INTO users (telegram_id, first_name, username, joined_date, last_activity) VALUES (?, ?, ?, ?, ?)",
                       (user_id, first_name, username, str(datetime.date.today()), str(datetime.datetime.now())))
        conn.commit()
    else:
        cursor.execute("UPDATE users SET last_activity = ? WHERE telegram_id = ?", (str(datetime.datetime.now()), user_id))
        conn.commit()
    conn.close()

    not_joined = check_subscription(user_id)
    if not_joined:
        markup = types.InlineKeyboardMarkup()
        for ch in not_joined:
            markup.add(types.InlineKeyboardButton(text="Obuna bo'lish 📢", url=f"https://t.me/{ch}"))
        markup.add(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub"))
        bot.send_message(message.chat.id, "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=markup)
        return

    welcome_text = f"""👋 *Assalomu alaykum, {first_name}!*

✨ *Ingliz tilini oson va qiziqarli o'rganish botiga xush kelibsiz!*

🎯 *Bot maqsadi:* 
Sizning ingliz tili so'z boyligingizni oshirish va grammatikani qisqa, tushunarli qilib, ovozli tarzda o'rgatish!

📌 *Qoidalar va Imkoniyatlar:*
🔹 *📖 So'zlar:* Har kuni *faqat 15 ta* yangi so'z beriladi (osondan qiyinga qarab).
🔹 *📝 Test:* Yodlagan so'zlaringiz bo'yicha o'zingizni sinaysiz va *XP (ball)* yig'asiz.
🔹 *📚 Grammatika:* Har kuni *faqat 1 ta* grammatika mavzusi (ovozli tushuntirish bilan) beriladi.
🔹 *🏆 Reyting:* Top foydalanuvchilar qatoriga kirish uchun har kuni faol bo'ling!

👇 *Boshlash uchun pastdagi menyudan birini tanlang:*"""
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check_sub(call):
    not_joined = check_subscription(call.from_user.id)
    if not_joined:
        bot.answer_callback_query(call.id, "Siz hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "Rahmat! Obuna tasdiqlandi.", show_alert=True)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Menyudan birini tanlang:", reply_markup=main_menu())

@bot.message_handler(commands=['admin'])
def admin_login(message):
    text = message.text.split()
    if len(text) > 1 and text[1] == config.ADMIN_PASSWORD:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_admin = 1 WHERE telegram_id = ?", (message.from_user.id,))
        conn.commit()
        conn.close()
        bot.reply_to(message, "Siz admin huquqini oldingiz!", reply_markup=admin_menu())
    else:
        bot.reply_to(message, "Parol noto'g'ri yoki yozilmadi. Foydalanish: /admin parol")

# --- ADMIN FUNKSIYALARI ---
def is_admin(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE telegram_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res and res[0] == 1

def set_state(user_id, state):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO user_states (telegram_id, state) VALUES (?, ?)", (user_id, state))
    conn.commit()
    conn.close()

def get_state(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT state FROM user_states WHERE telegram_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

def clear_state(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_states WHERE telegram_id = ?", (user_id,))
    conn.commit()
    conn.close()

@bot.message_handler(func=lambda m: m.text == "⬅️ Asosiy menyu")
def back_main(message):
    clear_state(message.from_user.id)
    bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "➕ Kanal qo'shish")
def add_channel_start(message):
    if not is_admin(message.from_user.id): return
    set_state(message.from_user.id, "admin_add_channel")
    bot.send_message(message.chat.id, "Kanal usernamesini yuboring (@ belgisiz, masalan: my_channel):", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_add_channel")
def add_channel_finish(message):
    channel = message.text.replace('@', '').strip()
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO channels (channel_username, channel_name) VALUES (?, ?)", (channel, channel))
        conn.commit()
        bot.send_message(message.chat.id, f"✅ Kanal qo'shildi: @{channel}", reply_markup=admin_menu())
    except sqlite3.IntegrityError:
        bot.send_message(message.chat.id, "Bu kanal allaqachon qo'shilgan.", reply_markup=admin_menu())
    finally:
        conn.close()
    clear_state(message.from_user.id)

@bot.message_handler(func=lambda m: m.text == "➖ Kanal o'chirish")
def del_channel_start(message):
    if not is_admin(message.from_user.id): return
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT channel_username FROM channels")
    channels = cursor.fetchall()
    conn.close()
    
    if not channels:
        bot.send_message(message.chat.id, "Kanallar yo'q.")
        return
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for (ch,) in channels:
        markup.add(f"❌ {ch}")
    markup.add("⬅️ Asosiy menyu")
    set_state(message.from_user.id, "admin_del_channel")
    bot.send_message(message.chat.id, "O'chirmoqchi bo'lgan kanalni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_del_channel")
def del_channel_finish(message):
    if message.text == "⬅️ Asosiy menyu":
        back_main(message)
        return
    channel = message.text.replace('❌ ', '').strip()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM channels WHERE channel_username = ?", (channel,))
    conn.commit()
    conn.close()
    clear_state(message.from_user.id)
    bot.send_message(message.chat.id, f"✅ Kanal o'chirildi: {channel}", reply_markup=admin_menu())

@bot.message_handler(func=lambda m: m.text == "📢 Xabar tarqatish")
def broadcast_start(message):
    if not is_admin(message.from_user.id): return
    set_state(message.from_user.id, "admin_broadcast")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⬅️ Asosiy menyu")
    bot.send_message(message.chat.id, "Tarqatmoqchi bo'lgan xabaringizni yuboring (rasm, video yoki matn):", reply_markup=markup)

@bot.message_handler(content_types=['text', 'photo', 'video', 'document'], func=lambda m: get_state(m.from_user.id) == "admin_broadcast")
def broadcast_finish(message):
    if message.text == "⬅️ Asosiy menyu":
        back_main(message)
        return
        
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users")
    users = cursor.fetchall()
    conn.close()
    
    bot.send_message(message.chat.id, f"⏳ Tarqatish boshlandi... Jami foydalanuvchilar: {len(users)}")
    clear_state(message.from_user.id)
    
    success = 0
    for (uid,) in users:
        try:
            bot.copy_message(chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id)
            success += 1
        except Exception:
            pass
            
    bot.send_message(message.chat.id, f"✅ Tarqatish tugadi. {success} ta odamga bordi.", reply_markup=admin_menu())

@bot.message_handler(func=lambda m: m.text == "➕ So'z qo'shish")
def add_word_start(message):
    if not is_admin(message.from_user.id): return
    set_state(message.from_user.id, "admin_add_word_en")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⬅️ Asosiy menyu")
    bot.send_message(message.chat.id, "Yangi so'zni Ingliz tilida kiriting:", reply_markup=markup)

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_add_word_en")
def add_word_uz(message):
    if message.text == "⬅️ Asosiy menyu":
        back_main(message)
        return
    # Temporarily store english word in state data
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_states SET state = ?, data = ? WHERE telegram_id = ?", ("admin_add_word_uz", message.text, message.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Yaxshi! Endi '{message.text}' so'zining O'zbekcha tarjimasini kiriting:")

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_add_word_uz")
def add_word_finish(message):
    if message.text == "⬅️ Asosiy menyu":
        back_main(message)
        return
    uz_word = message.text
    
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM user_states WHERE telegram_id = ?", (message.from_user.id,))
    en_word = cursor.fetchone()[0]
    
    cursor.execute("INSERT INTO words (english_word, uzbek_translation) VALUES (?, ?)", (en_word, uz_word))
    conn.commit()
    conn.close()
    
    clear_state(message.from_user.id)
    bot.send_message(message.chat.id, f"✅ So'z qo'shildi:\n🇬🇧 {en_word} - 🇺🇿 {uz_word}", reply_markup=admin_menu())

@bot.message_handler(func=lambda m: m.text == "➕ Grammatika qo'shish")
def add_grammar_start(message):
    if not is_admin(message.from_user.id): return
    set_state(message.from_user.id, "admin_add_grammar_title")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⬅️ Asosiy menyu")
    bot.send_message(message.chat.id, "Grammatika mavzusini kiriting (masalan: Present Simple):", reply_markup=markup)

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_add_grammar_title")
def add_grammar_content(message):
    if message.text == "⬅️ Asosiy menyu":
        back_main(message)
        return
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_states SET state = ?, data = ? WHERE telegram_id = ?", ("admin_add_grammar_content", message.text, message.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Mavzu saqlandi. Endi '{message.text}' uchun qoidalar va misollarni yozing (Darak, Inkor, So'roq):")

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_add_grammar_content")
def add_grammar_finish(message):
    if message.text == "⬅️ Asosiy menyu":
        back_main(message)
        return
    content = message.text
    
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM user_states WHERE telegram_id = ?", (message.from_user.id,))
    title = cursor.fetchone()[0]
    
    cursor.execute("INSERT INTO grammar (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()
    
    clear_state(message.from_user.id)
    bot.send_message(message.chat.id, f"✅ Grammatika qo'shildi:\n{title}", reply_markup=admin_menu())

@bot.message_handler(func=lambda m: m.text == "📊 Foydalanuvchilar")
def admin_users(message):
    if not is_admin(message.from_user.id): return
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id, first_name, username, xp FROM users ORDER BY xp DESC")
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        bot.send_message(message.chat.id, "Foydalanuvchilar yo'q.")
        return
        
    text = f"👥 Jami foydalanuvchilar: {len(users)}\n\n"
    for tg_id, name, username, xp in users[:100]: # top 100 to avoid message size limit
        # Remove html tags from name just in case
        name = str(name).replace('<', '').replace('>', '')
        if username and username.strip():
            link = f"@{username}"
        else:
            link = f"<a href='tg://user?id={tg_id}'>{tg_id}</a>"
        text += f"👤 {name} | {link} | ⭐ {xp} XP\n"
        
    for i in range(0, len(text), 4000):
        bot.send_message(message.chat.id, text[i:i+4000], parse_mode='HTML')

# --- USER FUNKSIYALARI ---

def get_daily_words(user_id=None):
    today = str(datetime.date.today())
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT w.english_word, w.uzbek_translation FROM daily_words d JOIN words w ON d.word_id = w.id WHERE d.date = ?", (today,))
    words = cursor.fetchall()
    
    if not words:
        cursor.execute("SELECT id, english_word, uzbek_translation FROM words WHERE id NOT IN (SELECT word_id FROM daily_words) ORDER BY RANDOM() LIMIT 15")
        rows = cursor.fetchall()
        
        if len(rows) < 15:
            # Notify admins
            cursor.execute("SELECT telegram_id FROM users WHERE is_admin = 1")
            admins = cursor.fetchall()
            for (admin_id,) in admins:
                try:
                    bot.send_message(admin_id, "⚠️ DIQQAT! BAZADA YANGI SO'ZLAR TUGAMOQDA! Iltimos, admin paneldan so'zlar kiritishni boshlang.")
                except: pass
                
        for row in rows:
            cursor.execute("INSERT INTO daily_words (date, word_id) VALUES (?, ?)", (today, row[0]))
            words.append((row[1], row[2]))
        conn.commit()
    conn.close()
    return words

@bot.message_handler(func=lambda m: m.text == "📚 Grammatika")
def send_grammar(message):
    user_id = message.from_user.id
    today = str(datetime.date.today())
    
    conn = get_conn()
    cursor = conn.cursor()
    
    # Check grammar progress
    cursor.execute("SELECT current_grammar_id, last_date FROM user_grammar WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    
    if not res:
        cursor.execute("INSERT INTO user_grammar (user_id, current_grammar_id, last_date) VALUES (?, 1, ?)", (user_id, today))
        grammar_id = 1
        last_date = today
    else:
        grammar_id, last_date = res
        if last_date != today:
            grammar_id += 1
            cursor.execute("UPDATE user_grammar SET current_grammar_id = ?, last_date = ? WHERE user_id = ?", (grammar_id, today, user_id))
            
    conn.commit()
    
    cursor.execute("SELECT title, content, voice_file_id FROM grammar WHERE id = ?", (grammar_id,))
    grammar_row = cursor.fetchone()
    
    if not grammar_row:
        conn.close()
        bot.send_message(message.chat.id, "Barcha grammatika darslarini tugatdingiz! Tez orada yangilari qo'shiladi.")
        return
        
    title, content, voice_file_id = grammar_row
    text = f"📚 Bugungi Grammatika Darsi:\n\n📌 *{title}*\n\n{content}"
    
    msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')
    
    # Send voice
    try:
        bot.send_chat_action(message.chat.id, 'record_voice')
        if voice_file_id:
            bot.send_voice(message.chat.id, voice_file_id, caption="🔊 Qoidalarni ovozli eshiting!")
            conn.close()
        else:
            voice_text = f"Today's grammar lesson is: {title}. {content}"
            tts = gTTS(text=voice_text, lang='en', slow=False)
            voice_filename = f"grammar_{grammar_id}.ogg"
            tts.save(voice_filename)
            
            with open(voice_filename, 'rb') as voice:
                sent_msg = bot.send_voice(message.chat.id, voice, caption="🔊 Qoidalarni ovozli eshiting!")
                new_file_id = sent_msg.voice.file_id
                cursor.execute("UPDATE grammar SET voice_file_id = ? WHERE id = ?", (new_file_id, grammar_id))
                conn.commit()
                
            os.remove(voice_filename)
            conn.close()
    except Exception as e:
        conn.close()
        print(f"TTS Error: {e}")

@bot.message_handler(func=lambda m: m.text == "📖 So'zlar")
def send_words(message):
    words = get_daily_words(message.from_user.id)
    
    if not words:
        bot.send_message(message.chat.id, "Hozircha bazada so'zlar qolmadi, adminga xabar berildi.")
        return
        
    text = f"📚 Bugungi kunning 15 ta so'zi ({str(datetime.date.today())}):\n\n"
    for i, (en, uz) in enumerate(words, 1):
        text += f"{i}. 🇬🇧 {en} - 🇺🇿 {uz}\n"
    text += "\nQolgan so'zlar ertaga ochiladi. Ularni yodlang va '📝 Test ishlash' bo'limida o'zingizni sinang!"    
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "📝 Test ishlash")
def send_test(message):
    conn = get_conn()
    cursor = conn.cursor()
    # ONLY generate tests from words that were sent as daily words!
    cursor.execute("SELECT w.english_word, w.uzbek_translation FROM daily_words d JOIN words w ON d.word_id = w.id ORDER BY RANDOM() LIMIT 4")
    words = cursor.fetchall()
    conn.close()
    
    if len(words) < 4:
        bot.send_message(message.chat.id, "Test tuzish uchun yetarli so'z yo'q (kamida 4 ta).")
        return
        
    correct_word = words[0]
    question = f"🇬🇧 '{correct_word[0]}' so'zining tarjimasi qaysi?"
    
    options = [w[1] for w in words]
    import random
    random.shuffle(options)
    
    markup = types.InlineKeyboardMarkup()
    for opt in options:
        # data: test_ok or test_no
        data = "test_ok" if opt == correct_word[1] else "test_no"
        markup.add(types.InlineKeyboardButton(text=opt, callback_data=data))
    
    # Stop button
    markup.add(types.InlineKeyboardButton(text="❌ To'xtatish", callback_data="test_stop"))
        
    bot.send_message(message.chat.id, question, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("test_"))
def handle_test(call):
    if call.data == "test_stop":
        bot.edit_message_text("🛑 Test to'xtatildi. Asosiy menyudan bo'lim tanlang.", call.message.chat.id, call.message.message_id)
        return
        
    if call.data == "test_ok":
        bot.answer_callback_query(call.id, "✅ To'g'ri topdingiz! +5 XP", show_alert=False)
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET xp = xp + 5 WHERE telegram_id = ?", (call.from_user.id,))
        conn.commit()
        conn.close()
    else:
        bot.answer_callback_query(call.id, "❌ Noto'g'ri!", show_alert=False)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_test(call.message) # send another test

@bot.message_handler(func=lambda m: m.text == "🎁 Bonus")
def get_bonus(message):
    user_id = message.from_user.id
    today = str(datetime.date.today())
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT last_bonus_date FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user and user[0] == today:
        bot.send_message(message.chat.id, "🎁 Siz bugungi bonusni olib bo'ldingiz! Ertaga yana urinib ko'ring.")
    else:
        bonus_xp = random.randint(1, 10)
        cursor.execute("UPDATE users SET xp = xp + ?, last_bonus_date = ? WHERE telegram_id = ?", (bonus_xp, today, user_id))
        conn.commit()
        bot.send_message(message.chat.id, f"🎁 Tabriklaymiz! Sizga tasodifiy {bonus_xp} XP bonus berildi!")
        
    conn.close()

@bot.message_handler(func=lambda m: m.text == "👤 Profil")
def profile(message):
    user_id = message.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT xp, joined_date FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        text = f"👤 Sizning profilingiz:\n\n⭐ XP: {user[0]}\n📅 Qo'shilgan sana: {user[1]}"
        bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🏆 Reyting")
def rating(message):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, xp FROM users ORDER BY xp DESC LIMIT 10")
    top = cursor.fetchall()
    conn.close()
    
    text = "🏆 Top 10 o'quvchilar:\n\n"
    for i, (name, xp) in enumerate(top, 1):
        text += f"{i}. {name} - {xp} XP\n"
    bot.send_message(message.chat.id, text)

# For running scheduled jobs
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(1)
    threading.Thread(target=run_scheduler, daemon=True).start()
    print("Bot is running via Long Polling...")
    bot.infinity_polling(skip_pending=True)
