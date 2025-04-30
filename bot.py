import telebot
import subprocess
from flask import Flask
from threading import Thread

# ======== إعدادات ========
TELEGRAM_BOT_TOKEN = '7471008788:AAFBBdGspKxJPYGAgITKeWt6fsNAm6ufALg'
STREAM_URL = 'rtmps://live-api-s.facebook.com:443/rtmp/'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# نحفظو الحالات ديال كل مستخدم
user_states = {}

# ======== سيرفر صغير باش يبقى البوت خدام ========
app = Flask('')

@app.route('/')
def home():
    return "✅ البوت خدام مزيان."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()

# ======== التعامل مع الأوامر ========

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلاً! أرسل رابط الفيديو باش نبثوه على Facebook Live.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    text = message.text

    if user_id in user_states and user_states[user_id]['waiting_for'] == 'stream_key':
        # المستخدم صيفط Stream Key
        stream_key = text
        video_url = user_states[user_id]['video_url']
        bot.send_message(user_id, "🚀 كنبدأو البث المباشر...")

        # إعداد ffmpeg للبث
        command = [
            'ffmpeg',
            '-re',
            '-i', video_url,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-f', 'flv',
            STREAM_URL + stream_key
        ]

        try:
            subprocess.run(command)
            bot.send_message(user_id, "✅ سالينا البث المباشر.")
        except Exception as e:
            bot.send_message(user_id, f"❌ وقع خطأ: {e}")

        # نحيد حالة المستخدم
        del user_states[user_id]

    else:
        # أول رسالة = رابط الفيديو
        user_states[user_id] = {
            'waiting_for': 'stream_key',
            'video_url': text
        }
        bot.send_message(user_id, "📥 توصلت بالرابط.\nصيفط ليا دابا Stream Key ديالك ديال Facebook.")

# ======== تشغيل البوت ========
keep_alive()
bot.polling()
