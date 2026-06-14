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
    markup.row("📚 Grammatika", "👤 Profil")
    markup.row("🎁 Bonus", "🏆 Reyting")
    markup.row("⚙️ Tilni tanlash")
    return markup

def admin_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📢 Xabar tarqatish", "📊 Foydalanuvchilar")
    markup.row("📈 Umumiy Statistika", "👤 Boshqaruv (Ban/Unban)")
    markup.row("➕ Kanal qo'shish", "➖ Kanal o'chirish")
    markup.row("➕ So'z qo'shish", "➕ Grammatika qo'shish")
    markup.row("⬅️ Asosiy menyu")
    return markup

def get_user_lang(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT target_lang FROM users WHERE telegram_id = ?", (user_id,))
        res = cursor.fetchone()
        return res[0] if res and res[0] else 'en'
    except:
        return 'en'
    finally:
        conn.close()

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
        cursor.execute("INSERT INTO users (telegram_id, first_name, username, joined_date, last_activity, target_lang) VALUES (?, ?, ?, ?, ?, ?)",
                       (user_id, first_name, username, str(datetime.date.today()), str(datetime.datetime.now()), 'en'))
        conn.commit()
    else:
        cursor.execute("UPDATE users SET last_activity = ? WHERE telegram_id = ?", (str(datetime.datetime.now()), user_id))
        conn.commit()
    conn.close()

    if is_user_blocked(user_id):
        bot.send_message(message.chat.id, "Sizning hisobingiz bloklangan. Botdan foydalana olmaysiz.")
        return

    not_joined = check_subscription(user_id)
    if not_joined:
        markup = types.InlineKeyboardMarkup()
        for ch in not_joined:
            markup.add(types.InlineKeyboardButton(text="Obuna bo'lish 📢", url=f"https://t.me/{ch}"))
        markup.add(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub"))
        bot.send_message(message.chat.id, "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=markup)
        return

    welcome_text = f"""👋 *Assalomu alaykum, {first_name}!*

✨ *Poliglot botiga xush kelibsiz!*
Bu yerda siz *Ingliz, Rus, Koreys va Turk* tillarini oson va qiziqarli o'rganishingiz mumkin!

━━━━━━━━━━━━━━━━━━━━
🎯 *Bot maqsadi:* 
So'z boyligingizni oshirish va grammatikani qisqa, tushunarli qilib o'rgatish! 
Barcha tushuntirishlar o'zingiz tanlagan tilga moslab qisqa va aniq yetkaziladi.

📌 *Imkoniyatlar:*
🔹 *📖 So'zlar:* Har kuni o'zingiz tanlagan tilda *15 ta* yangi so'z.
🔹 *📝 Test:* Yodlagan so'zlaringiz bo'yicha takrorlanmaydigan va tasodifiy testlar!
🔹 *📚 Grammatika:* Har kuni *1 ta* yangi qoida.
🔹 *🏆 Profil & Reyting:* XP to'plab, top o'quvchilar qatoriga kiring!
━━━━━━━━━━━━━━━━━━━━

👇 *Boshlash uchun pastdagi menyudan foydalaning (Tilni o'zgartirish uchun "⚙️ Tilni tanlash" ni bosing):*"""
    
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

@bot.message_handler(func=lambda m: m.text == "⚙️ Tilni tanlash")
def choose_lang_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🇬🇧 Ingliz tili", "🇷🇺 Rus tili")
    markup.row("🇰🇷 Koreys tili", "🇹🇷 Turk tili")
    markup.row("⬅️ Asosiy menyu")
    bot.send_message(message.chat.id, "👇 O'rganmoqchi bo'lgan tilingizni tanlang:", reply_markup=markup)

lang_map = {
    "🇬🇧 Ingliz tili": "en",
    "🇷🇺 Rus tili": "ru",
    "🇰🇷 Koreys tili": "kr",
    "🇹🇷 Turk tili": "tr"
}

@bot.message_handler(func=lambda m: m.text in lang_map.keys())
def set_language(message):
    lang_code = lang_map[message.text]
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET target_lang = ? WHERE telegram_id = ?", (lang_code, message.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"✅ O'rganish tili *{message.text}* ga o'zgartirildi!\nEndi so'zlar va testlar shu tilda beriladi.", parse_mode="Markdown", reply_markup=main_menu())

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
    set_state(message.from_user.id, "admin_add_word_lang")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("en", "ru", "kr", "tr")
    markup.add("⬅️ Asosiy menyu")
    bot.send_message(message.chat.id, "Qaysi til uchun so'z qo'shasiz? (en, ru, kr, tr):", reply_markup=markup)

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_add_word_lang")
def add_word_en(message):
    if message.text == "⬅️ Asosiy menyu":
        back_main(message)
        return
    lang = message.text
    if lang not in ['en', 'ru', 'kr', 'tr']:
        bot.send_message(message.chat.id, "Iltimos, faqat menyudagi tillardan birini tanlang.")
        return
        
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_states SET state = ?, data = ? WHERE telegram_id = ?", ("admin_add_word_foreign", lang, message.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Yangi so'zni *{lang.upper()}* tilida kiriting:", parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_add_word_foreign")
def add_word_uz(message):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM user_states WHERE telegram_id = ?", (message.from_user.id,))
    lang = cursor.fetchone()[0]
    
    new_data = f"{lang}|{message.text}"
    cursor.execute("UPDATE user_states SET state = ?, data = ? WHERE telegram_id = ?", ("admin_add_word_uz", new_data, message.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Yaxshi! Endi '{message.text}' so'zining O'zbekcha tarjimasini kiriting:")

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_add_word_uz")
def add_word_finish(message):
    uz_word = message.text
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM user_states WHERE telegram_id = ?", (message.from_user.id,))
    data = cursor.fetchone()[0]
    lang, foreign_word = data.split('|')
    
    cursor.execute("INSERT INTO words (english_word, uzbek_translation, lang) VALUES (?, ?, ?)", (foreign_word, uz_word, lang))
    conn.commit()
    conn.close()
    
    clear_state(message.from_user.id)
    flags = {'en': '🇬🇧', 'ru': '🇷🇺', 'kr': '🇰🇷', 'tr': '🇹🇷'}
    flag = flags.get(lang, '🌎')
    bot.send_message(message.chat.id, f"✅ So'z qo'shildi:\n{flag} {foreign_word} - 🇺🇿 {uz_word}", reply_markup=admin_menu())

@bot.message_handler(func=lambda m: m.text == "➕ Grammatika qo'shish")
def add_grammar_start(message):
    if not is_admin(message.from_user.id): return
    set_state(message.from_user.id, "admin_add_grammar_lang")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("en", "ru", "kr", "tr")
    markup.add("⬅️ Asosiy menyu")
    bot.send_message(message.chat.id, "Qaysi til uchun grammatika qo'shasiz? (en, ru, kr, tr):", reply_markup=markup)

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_add_grammar_lang")
def add_grammar_title(message):
    if message.text == "⬅️ Asosiy menyu":
        back_main(message)
        return
    lang = message.text
    if lang not in ['en', 'ru', 'kr', 'tr']:
        bot.send_message(message.chat.id, "Iltimos, faqat menyudagi tillardan birini tanlang.")
        return
        
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_states SET state = ?, data = ? WHERE telegram_id = ?", ("admin_add_grammar_title", lang, message.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"*{lang.upper()}* tili uchun Grammatika mavzusini kiriting (masalan: Present Simple):", parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_add_grammar_title")
def add_grammar_content(message):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM user_states WHERE telegram_id = ?", (message.from_user.id,))
    lang = cursor.fetchone()[0]
    
    new_data = f"{lang}|{message.text}"
    cursor.execute("UPDATE user_states SET state = ?, data = ? WHERE telegram_id = ?", ("admin_add_grammar_content", new_data, message.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Mavzu saqlandi. Endi '{message.text}' uchun qoidalar va misollarni yozing:")

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_add_grammar_content")
def add_grammar_finish(message):
    content = message.text
    
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM user_states WHERE telegram_id = ?", (message.from_user.id,))
    data = cursor.fetchone()[0]
    lang, title = data.split('|')
    
    cursor.execute("INSERT INTO grammar (title, content, lang) VALUES (?, ?, ?)", (title, content, lang))
    conn.commit()
    conn.close()
    
    clear_state(message.from_user.id)
    bot.send_message(message.chat.id, f"✅ Grammatika qo'shildi ({lang.upper()}):\n{title}", reply_markup=admin_menu())

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
    for tg_id, name, username, xp in users[:100]: 
        name = str(name).replace('<', '').replace('>', '')
        if username and username.strip():
            link = f"@{username}"
        else:
            link = f"<a href='tg://user?id={tg_id}'>{tg_id}</a>"
        text += f"👤 {name} (ID: {tg_id}) | {link} | ⭐ {xp} XP\n"
        
    for i in range(0, len(text), 4000):
        bot.send_message(message.chat.id, text[i:i+4000], parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "📈 Umumiy Statistika")
def admin_stats(message):
    if not is_admin(message.from_user.id): return
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT target_lang, count(*) FROM users GROUP BY target_lang")
    lang_stats = cursor.fetchall()
    
    cursor.execute("SELECT lang, count(*) FROM words GROUP BY lang")
    word_stats = cursor.fetchall()
    
    cursor.execute("SELECT count(*) FROM channels")
    channels = cursor.fetchone()[0]
    conn.close()
    
    text = f"📈 *Bot Statistikasi*\n\n"
    text += f"👥 Jami foydalanuvchilar: {total_users}\n"
    text += f"📢 Jami kanallar: {channels}\n\n"
    
    text += "🌍 *Tillar bo'yicha o'quvchilar:*\n"
    for lang, count in lang_stats:
        l_name = lang.upper() if lang else "Noma'lum"
        text += f" - {l_name}: {count} ta\n"
        
    text += "\n📚 *Bazada so'zlar:*\n"
    for lang, count in word_stats:
        l_name = lang.upper() if lang else "Noma'lum"
        text += f" - {l_name}: {count} ta\n"
        
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👤 Boshqaruv (Ban/Unban)")
def admin_manage_users(message):
    if not is_admin(message.from_user.id): return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚫 Ban qilish", "✅ Bandan chiqarish")
    markup.row("💬 Shaxsiy xabar yozish")
    markup.row("⬅️ Admin menyu")
    bot.send_message(message.chat.id, "Tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "⬅️ Admin menyu")
def back_admin(message):
    if not is_admin(message.from_user.id): return
    clear_state(message.from_user.id)
    bot.send_message(message.chat.id, "Admin menyusiga qaytdingiz.", reply_markup=admin_menu())

@bot.message_handler(func=lambda m: m.text == "🚫 Ban qilish")
def admin_ban(message):
    if not is_admin(message.from_user.id): return
    set_state(message.from_user.id, "admin_ban_user")
    bot.send_message(message.chat.id, "Foydalanuvchi ID sini yuboring:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_ban_user")
def admin_ban_finish(message):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_blocked = 1 WHERE telegram_id = ?", (message.text,))
    conn.commit()
    conn.close()
    clear_state(message.from_user.id)
    bot.send_message(message.chat.id, "Foydalanuvchi bloklandi!", reply_markup=admin_menu())

@bot.message_handler(func=lambda m: m.text == "✅ Bandan chiqarish")
def admin_unban(message):
    if not is_admin(message.from_user.id): return
    set_state(message.from_user.id, "admin_unban_user")
    bot.send_message(message.chat.id, "Foydalanuvchi ID sini yuboring:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_unban_user")
def admin_unban_finish(message):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_blocked = 0 WHERE telegram_id = ?", (message.text,))
    conn.commit()
    conn.close()
    clear_state(message.from_user.id)
    bot.send_message(message.chat.id, "Foydalanuvchi bandan chiqarildi!", reply_markup=admin_menu())

@bot.message_handler(func=lambda m: m.text == "💬 Shaxsiy xabar yozish")
def admin_pm(message):
    if not is_admin(message.from_user.id): return
    set_state(message.from_user.id, "admin_pm_id")
    bot.send_message(message.chat.id, "Xabar yubormoqchi bo'lgan foydalanuvchi ID sini kiriting:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_pm_id")
def admin_pm_text(message):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_states SET state = ?, data = ? WHERE telegram_id = ?", ("admin_pm_text", message.text, message.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"ID {message.text} ga xabaringizni yozing:")

@bot.message_handler(func=lambda m: get_state(m.from_user.id) == "admin_pm_text")
def admin_pm_finish(message):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM user_states WHERE telegram_id = ?", (message.from_user.id,))
    target_id = cursor.fetchone()[0]
    conn.close()
    clear_state(message.from_user.id)
    try:
        bot.send_message(target_id, f"🔔 *Admindan xabar:*\n\n{message.text}", parse_mode="Markdown")
        bot.send_message(message.chat.id, "Xabar yuborildi!", reply_markup=admin_menu())
    except Exception as e:
        bot.send_message(message.chat.id, f"Xato yuz berdi: {e}", reply_markup=admin_menu())

def is_user_blocked(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT is_blocked FROM users WHERE telegram_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res and res[0] == 1

# --- USER FUNKSIYALARI ---

def get_daily_words(user_id):
    today = str(datetime.date.today())
    lang = get_user_lang(user_id)
    conn = get_conn()
    cursor = conn.cursor()
    
    # daily_words has lang column now
    cursor.execute("SELECT w.id, w.english_word, w.uzbek_translation FROM daily_words d JOIN words w ON d.word_id = w.id WHERE d.date = ? AND w.lang = ?", (today, lang))
    words = cursor.fetchall()
    
    if not words:
        cursor.execute("SELECT id, english_word, uzbek_translation FROM words WHERE lang = ? AND id NOT IN (SELECT word_id FROM daily_words) ORDER BY RANDOM() LIMIT 15", (lang,))
        rows = cursor.fetchall()
        
        if len(rows) < 15:
            cursor.execute("SELECT telegram_id FROM users WHERE is_admin = 1")
            admins = cursor.fetchall()
            for (admin_id,) in admins:
                try:
                    bot.send_message(admin_id, f"⚠️ DIQQAT! {lang.upper()} tili uchun bazada YANGI SO'ZLAR TUGAMOQDA! Iltimos, admin paneldan so'zlar kiritishni boshlang.")
                except: pass
                
        for row in rows:
            cursor.execute("INSERT INTO daily_words (date, word_id, lang) VALUES (?, ?, ?)", (today, row[0], lang))
            words.append(row)
        conn.commit()
    conn.close()
    return words

@bot.message_handler(func=lambda m: m.text == "📚 Grammatika")
def send_grammar(message):
    user_id = message.from_user.id
    user_lang = get_user_lang(user_id)
    today = str(datetime.date.today())
    
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT current_grammar_id, last_date FROM user_grammar WHERE user_id = ? AND lang = ?", (user_id, user_lang))
    res = cursor.fetchone()
    
    if not res:
        cursor.execute("SELECT id FROM grammar WHERE lang = ? ORDER BY id ASC LIMIT 1", (user_lang,))
        first_gram = cursor.fetchone()
        if not first_gram:
            bot.send_message(message.chat.id, "Hozircha ushbu til uchun grammatika mavzulari kiritilmagan.")
            conn.close()
            return
        grammar_id = first_gram[0]
        cursor.execute("INSERT INTO user_grammar (user_id, lang, current_grammar_id, last_date) VALUES (?, ?, ?, ?)", (user_id, user_lang, grammar_id, today))
        last_date = today
    else:
        grammar_id, last_date = res
        if last_date != today:
            cursor.execute("SELECT id FROM grammar WHERE lang = ? AND id > ? ORDER BY id ASC LIMIT 1", (user_lang, grammar_id))
            next_gram = cursor.fetchone()
            if next_gram:
                grammar_id = next_gram[0]
                cursor.execute("UPDATE user_grammar SET current_grammar_id = ?, last_date = ? WHERE user_id = ? AND lang = ?", (grammar_id, today, user_id, user_lang))
            
    conn.commit()
    
    cursor.execute("SELECT title, content, voice_file_id FROM grammar WHERE id = ?", (grammar_id,))
    grammar_row = cursor.fetchone()
    
    if not grammar_row:
        conn.close()
        bot.send_message(message.chat.id, "🎉 Barcha grammatika darslarini tugatdingiz! Tez orada yangilari qo'shiladi.")
        return
        
    title, content, voice_file_id = grammar_row
    text = f"📚 Bugungi Grammatika Darsi:\n\n📌 *{title}*\n\n{content}"
    
    msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')
    
    try:
        bot.send_chat_action(message.chat.id, 'record_voice')
        if voice_file_id:
            bot.send_voice(message.chat.id, voice_file_id, caption="🔊 Qoidalarni ovozli eshiting!")
            conn.close()
        else:
            voice_text = f"Today's lesson is: {title}. {content}" if user_lang == 'en' else f"{title}. {content}"
            lang_tts_map = {'en': 'en', 'ru': 'ru', 'kr': 'ko', 'tr': 'tr'}
            tts_lang = lang_tts_map.get(user_lang, 'en')
            
            tts = gTTS(text=voice_text, lang=tts_lang, slow=False)
            voice_filename = f"grammar_{grammar_id}_{user_lang}.ogg"
            tts.save(voice_filename)
            
            with open(voice_filename, 'rb') as voice:
                bot.send_voice(message.chat.id, voice, caption="🔊 Qoidalarni ovozli eshiting!")
                
            os.remove(voice_filename)
            conn.close()
    except Exception as e:
        conn.close()
        print(f"TTS Error: {e}")

@bot.message_handler(func=lambda m: m.text == "📖 So'zlar")
def send_words(message):
    lang = get_user_lang(message.from_user.id)
    words = get_daily_words(message.from_user.id)
    
    if not words:
        bot.send_message(message.chat.id, "Hozircha bazada ushbu til uchun so'zlar qolmadi, adminga xabar berildi.")
        return
        
    flags = {'en': '🇬🇧', 'ru': '🇷🇺', 'kr': '🇰🇷', 'tr': '🇹🇷'}
    flag = flags.get(lang, '🌎')
    
    text = f"📚 Bugungi kunning 15 ta so'zi ({str(datetime.date.today())}):\n\n"
    for i, (w_id, fw, uz) in enumerate(words, 1):
        text += f"{i}. {flag} {fw} - 🇺🇿 {uz}\n"
    text += "\nUlarni yodlang va '📝 Test ishlash' bo'limida o'zingizni sinang! Testlar qaytarilmaydi!"    
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "📝 Test ishlash")
def send_test(message):
    lang = get_user_lang(message.from_user.id)
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT xp FROM users WHERE telegram_id = ?", (message.from_user.id,))
    user_xp_row = cursor.fetchone()
    xp = user_xp_row[0] if user_xp_row else 0
    
    # Pick 1 correct word that user hasn't tested yet for this language
    cursor.execute("""
        SELECT id, english_word, uzbek_translation 
        FROM words 
        WHERE lang = ? AND id NOT IN (
            SELECT word_id FROM user_tests WHERE telegram_id = ?
        )
        ORDER BY RANDOM() LIMIT 1
    """, (lang, message.from_user.id))
    correct_row = cursor.fetchone()
    
    if not correct_row:
        bot.send_message(message.chat.id, "🎉 Tabriklaymiz! Siz ushbu tildagi barcha so'zlarni a'lo darajada o'zlashtirdingiz. Hozircha yangi testlar yo'q.")
        conn.close()
        return
        
    correct_id, correct_word, correct_translation = correct_row
    
    # Determine difficulty level
    if xp < 50:
        level = 1 # Easy: Foreign -> Uzbek
    elif xp < 150:
        level = 2 # Medium: Uzbek -> Foreign
    else:
        level = 3 # Hard: Type the foreign word
        
    flags = {'en': '🇬🇧', 'ru': '🇷🇺', 'kr': '🇰🇷', 'tr': '🇹🇷'}
    flag = flags.get(lang, '🌎')
    
    if level == 1:
        cursor.execute("SELECT uzbek_translation FROM words WHERE lang = ? AND id != ? ORDER BY RANDOM() LIMIT 3", (lang, correct_id))
        other_rows = cursor.fetchall()
        if len(other_rows) < 3:
            bot.send_message(message.chat.id, "Test tuzish uchun bazada yetarli so'z yo'q (kamida 4 ta kerak).")
            conn.close()
            return
            
        question = f"🔹 *1-Bosqich (Oson)*\n\n{flag} *{correct_word}* so'zining tarjimasi qaysi?"
        options = [correct_translation] + [r[0] for r in other_rows]
        random.shuffle(options)
        
        markup = types.InlineKeyboardMarkup()
        for opt in options:
            data = f"testok_{correct_id}" if opt == correct_translation else f"testno_{correct_id}"
            markup.add(types.InlineKeyboardButton(text=opt, callback_data=data))
        markup.add(types.InlineKeyboardButton(text="❌ To'xtatish", callback_data="test_stop"))
        bot.send_message(message.chat.id, question, reply_markup=markup, parse_mode="Markdown")
        
    elif level == 2:
        cursor.execute("SELECT english_word FROM words WHERE lang = ? AND id != ? ORDER BY RANDOM() LIMIT 3", (lang, correct_id))
        other_rows = cursor.fetchall()
        if len(other_rows) < 3:
            bot.send_message(message.chat.id, "Test tuzish uchun bazada yetarli so'z yo'q (kamida 4 ta kerak).")
            conn.close()
            return
            
        question = f"🔸 *2-Bosqich (O'rta)*\n\n🇺🇿 *{correct_translation}* so'zining {lang.upper()} tilidagi tarjimasi qaysi?"
        options = [correct_word] + [r[0] for r in other_rows]
        random.shuffle(options)
        
        markup = types.InlineKeyboardMarkup()
        for opt in options:
            data = f"testok_{correct_id}" if opt == correct_word else f"testno_{correct_id}"
            markup.add(types.InlineKeyboardButton(text=opt, callback_data=data))
        markup.add(types.InlineKeyboardButton(text="❌ To'xtatish", callback_data="test_stop"))
        bot.send_message(message.chat.id, question, reply_markup=markup, parse_mode="Markdown")
        
    elif level == 3:
        question = f"🔥 *3-Bosqich (Qiyin)*\n\n🇺🇿 *{correct_translation}* so'zining {lang.upper()} tilidagi tarjimasini yozib yuboring:"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="❌ To'xtatish", callback_data="test_stop"))
        bot.send_message(message.chat.id, question, reply_markup=markup, parse_mode="Markdown")
        set_state(message.from_user.id, f"test_typing_{correct_id}")
        
    conn.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("test"))
def handle_test(call):
    if call.data == "test_stop":
        clear_state(call.from_user.id)
        bot.edit_message_text("🛑 Test to'xtatildi. Asosiy menyudan bo'lim tanlang.", call.message.chat.id, call.message.message_id)
        return
        
    if call.data.startswith("testok_"):
        word_id = int(call.data.split("_")[1])
        bot.answer_callback_query(call.id, "✅ To'g'ri topdingiz! +5 XP", show_alert=False)
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET xp = xp + 5 WHERE telegram_id = ?", (call.from_user.id,))
        try:
            cursor.execute("INSERT INTO user_tests (telegram_id, word_id) VALUES (?, ?)", (call.from_user.id, word_id))
        except sqlite3.IntegrityError:
            pass # already in DB
        conn.commit()
        conn.close()
    elif call.data.startswith("testno_"):
        bot.answer_callback_query(call.id, "❌ Noto'g'ri!", show_alert=False)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Fix: call.message is the bot's message, so its from_user is the bot.
    # We must assign the actual user so send_test correctly identifies the language and XP.
    call.message.from_user = call.from_user
    send_test(call.message)

@bot.message_handler(func=lambda m: get_state(m.from_user.id) and get_state(m.from_user.id).startswith("test_typing_"))
def handle_typing_test(message):
    state = get_state(message.from_user.id)
    word_id = int(state.split("_")[2])
    
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT english_word, uzbek_translation FROM words WHERE id = ?", (word_id,))
    res = cursor.fetchone()
    
    if not res:
        clear_state(message.from_user.id)
        conn.close()
        return
        
    correct_word = res[0]
    
    if message.text.strip().lower() == correct_word.lower():
        bot.send_message(message.chat.id, "✅ *Ajoyib! To'g'ri topdingiz! +10 XP*", parse_mode="Markdown")
        cursor.execute("UPDATE users SET xp = xp + 10 WHERE telegram_id = ?", (message.from_user.id,))
        try:
            cursor.execute("INSERT INTO user_tests (telegram_id, word_id) VALUES (?, ?)", (message.from_user.id, word_id))
        except sqlite3.IntegrityError:
            pass
        conn.commit()
        clear_state(message.from_user.id)
        send_test(message)
    elif message.text in ["⬅️ Asosiy menyu", "📖 So'zlar", "📝 Test ishlash", "📚 Grammatika", "👤 Profil", "🎁 Bonus", "🏆 Reyting", "⚙️ Tilni tanlash"]:
        clear_state(message.from_user.id)
        bot.send_message(message.chat.id, "🛑 Test to'xtatildi.")
        if message.text == "⬅️ Asosiy menyu": back_main(message)
        elif message.text == "📖 So'zlar": send_words(message)
        elif message.text == "📝 Test ishlash": send_test(message)
        elif message.text == "📚 Grammatika": send_grammar(message)
        elif message.text == "👤 Profil": profile(message)
        elif message.text == "🎁 Bonus": get_bonus(message)
        elif message.text == "🏆 Reyting": rating(message)
        elif message.text == "⚙️ Tilni tanlash": choose_lang_start(message)
    else:
        bot.send_message(message.chat.id, f"❌ *Noto'g'ri!* (Yordam: so'z {len(correct_word)} ta harfdan iborat)\n\nYana urinib ko'ring yoki to'xtating.", parse_mode="Markdown")
        
    conn.close()

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
    cursor.execute("SELECT first_name, xp, joined_date, target_lang FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        name, xp, joined_date, lang = user
        flags = {'en': '🇬🇧 Ingliz', 'ru': '🇷🇺 Rus', 'kr': '🇰🇷 Koreys', 'tr': '🇹🇷 Turk'}
        lang_text = flags.get(lang, 'Noma\'lum')
        text = f"""👤 *Foydalanuvchi Profili:*

👤 *Ism:* {name}
⭐ *To'plangan XP:* {xp} ball
🌍 *O'rganilayotgan til:* {lang_text}
📅 *Qo'shilgan sana:* {joined_date}

_Ko'proq XP to'plash uchun testlarni yechishda davom eting!_"""
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏆 Reyting")
def rating(message):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, xp FROM users ORDER BY xp DESC LIMIT 10")
    top = cursor.fetchall()
    conn.close()
    
    text = "🏆 *Top 10 eng faol o'quvchilar:*\n\n"
    for i, (name, xp) in enumerate(top, 1):
        text += f"{i}. 👤 {name} - ⭐ {xp} XP\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    bot.remove_webhook()
    time.sleep(1)
    threading.Thread(target=run_scheduler, daemon=True).start()
    print("Poliglot bot is running via Long Polling...")
    bot.infinity_polling(skip_pending=True)
