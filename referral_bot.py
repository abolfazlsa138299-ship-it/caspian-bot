import os
import sqlite3
import json
import urllib.request
import urllib.parse
import urllib.error
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y")
MAIN_CHANNEL = "@proxy_caspian"
VIP_INVITE_LINK = "https://t.me/+kRHTDOtFljQ1NzBk"
SUB_LINK = "https://raw.githubusercontent.com/abolfazlsa138299-ship-it/caspian-bot/main/sub.txt"

# ----------------- وب‌سرور برای روشن ماندن ۲۴ ساعته -----------------
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Caspian Bot is Online!")

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheck)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

# ----------------- پایگاه داده (SQLite) -----------------
conn = sqlite3.connect("caspian_referral.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer_id INTEGER,
    joined_time INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id INTEGER,
    invited_id INTEGER UNIQUE,
    verified INTEGER DEFAULT 0
)
''')
conn.commit()

# ----------------- توابع کار با تلگرام -----------------
def telegram_api(method, data=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    if data:
        encoded_data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=encoded_data, headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"API Error ({method}): {e}")
        return None

def is_user_member(user_id):
    res = telegram_api("getChatMember", {"chat_id": MAIN_CHANNEL, "user_id": user_id})
    if res and res.get("ok"):
        status = res["result"].get("status")
        return status in ["member", "administrator", "creator"]
    return False

def get_referral_count(user_id):
    cursor.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND verified = 1", (user_id,))
    return cursor.fetchone()[0]

def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return telegram_api("sendMessage", payload)

def get_main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🔗 دریافت لینک دعوت اختصاصی", "callback_data": "get_link"}],
            [{"text": "📊 آمار دعوت و جوایز من", "callback_data": "my_stats"}],
            [{"text": "🎁 صندوق دریافت جوایز", "callback_data": "claim_rewards"}],
            [{"text": "⚡️ عضویت در کانال اصلی کاسپین", "url": "https://t.me/proxy_caspian"}]
        ]
    }

def handle_message(msg):
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")

    if text.startswith("/start"):
        parts = text.split()
        referrer_id = None
        if len(parts) > 1 and parts[1].startswith("ref_"):
            try:
                referrer_id = int(parts[1].replace("ref_", ""))
            except:
                referrer_id = None

        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (chat_id,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("INSERT INTO users (user_id, referrer_id, joined_time) VALUES (?, ?, ?)",
                           (chat_id, referrer_id, int(time.time())))
            conn.commit()

            if referrer_id and referrer_id != chat_id:
                if is_user_member(chat_id):
                    cursor.execute("INSERT OR IGNORE INTO referrals (referrer_id, invited_id, verified) VALUES (?, ?, 1)",
                                   (referrer_id, chat_id))
                    conn.commit()
                    count = get_referral_count(referrer_id)
                    send_message(referrer_id, f"🎉 <b>تبریک! یک نفر با لینک شما عضو شد.</b>\n👥 تعداد کل دعوت‌های تاییدشده شما: <b>{count}</b> نفر")
                    check_and_notify_rewards(referrer_id, count)
                else:
                    cursor.execute("INSERT OR IGNORE INTO referrals (referrer_id, invited_id, verified) VALUES (?, ?, 0)",
                                   (referrer_id, chat_id))
                    conn.commit()

        welcome_text = (
            "⚡️ <b>به ربات رسمی جوایز پروکسی کاسپین خوش آمدید!</b>\n\n"
            "🎁 <b>طرح دعوت و دریافت فیلترشکن رایگان (بدون قرعه‌کشی):</b>\n"
            "🔹 با دعوت <b>۵ نفر</b> ⬅️ عضویت در <b>کانال اختصاصی VIP کاسپین</b>\n"
            "🔹 با دعوت <b>۱۰ نفر</b> ⬅️ دریافت <b>لینک اشتراک هوشمند (Sub)</b> با آپدیت خودکار\n\n"
            "👇 از دکمه‌های زیر برای دریافت لینک دعوت و مشاهده آمار خود استفاده کنید:"
        )
        send_message(chat_id, welcome_text, get_main_keyboard())

def check_and_notify_rewards(user_id, count):
    if count == 5:
        send_message(user_id, (
            "🎉🔥 <b>تبریک! شما به ۵ دعوت رسیدید!</b>\n\n"
            "🎁 جایزه اول شما فعال شد: ورود به کانال اختصاصی VIP کاسپین\n"
            f"🔗 <b>لینک ورود مستقیم:</b>\n{VIP_INVITE_LINK}"
        ))
    elif count == 10:
        send_message(user_id, (
            "🏆🔥 <b>شاهکار کردید! شما به ۱۰ دعوت رسیدید!</b>\n\n"
            "🎁 جایزه دوم شما: <b>لینک ساب‌اسکریپشن هوشمند کاسپین</b>\n"
            "این لینک را داخل برنامه V2rayNG / Hiddify / v2box قرار دهید:\n\n"
            f"<code>{SUB_LINK}</code>\n\n"
            "🔄 با هر بار زدن دکمه Update در برنامه، کانفیگ‌های تازه و پرسرعت لود می‌شوند."
        ))

def handle_callback(cb):
    cb_id = cb["id"]
    chat_id = cb["message"]["chat"]["id"]
    data = cb.get("data", "")
    bot_username = "CaspianProxyBot"

    cursor.execute("SELECT referrer_id FROM referrals WHERE invited_id = ? AND verified = 0", (chat_id,))
    pending = cursor.fetchone()
    if pending and is_user_member(chat_id):
        ref_id = pending[0]
        cursor.execute("UPDATE referrals SET verified = 1 WHERE invited_id = ?", (chat_id,))
        conn.commit()
        count = get_referral_count(ref_id)
        send_message(ref_id, f"🎉 <b>یک کاربر دعوت‌شده عضو کانال شد!</b>\n👥 کل دعوت‌های شما: <b>{count}</b> نفر")
        check_and_notify_rewards(ref_id, count)

    if data == "get_link":
        ref_link = f"https://t.me/{bot_username}?start=ref_{chat_id}"
        msg = (
            "🔗 <b>لینک دعوت اختصاصی شما:</b>\n\n"
            f"<code>{ref_link}</code>\n\n"
            "📌 این لینک را برای دوستان، گروه‌ها یا مخاطبین خود بفرستید.\n"
            "به محض اینکه وارد ربات و عضو کانال @proxy_caspian شوند، امتیاز برای شما ثبت می‌شود!"
        )
        send_message(chat_id, msg, get_main_keyboard())

    elif data == "my_stats":
        count = get_referral_count(chat_id)
        remain_vip = max(0, 5 - count)
        remain_sub = max(0, 10 - count)
        
        status_vip = "✅ دریافت شده" if count >= 5 else f"⏳ {remain_vip} نفر مانده"
        status_sub = "✅ دریافت شده" if count >= 10 else f"⏳ {remain_sub} نفر مانده"

        msg = (
            "📊 <b>آمار و وضعیت زیرمجموعه‌های شما:</b>\n\n"
            f"👥 تعداد دعوت‌های تاییدشده: <b>{count} نفر</b>\n\n"
            f"🎁 <b>کانال اختصاصی VIP (۵ دعوت):</b> {status_vip}\n"
            f"🎁 <b>لینک ساب هوشمند (۱۰ دعوت):</b> {status_sub}\n"
        )
        send_message(chat_id, msg, get_main_keyboard())

    elif data == "claim_rewards":
        count = get_referral_count(chat_id)
        if count < 5:
            msg = f"❌ شما هنوز به حداقل دعوت (۵ نفر) نرسیده‌اید.\nتعداد دعوت فعلی شما: <b>{count}</b> نفر"
        elif 5 <= count < 10:
            msg = (
                "🎁 <b>جایزه سطح ۱ شما فعال است:</b>\n\n"
                f"🔗 ورود به کانال اختصاصی VIP:\n{VIP_INVITE_LINK}\n\n"
                f"💡 با دعوت <b>{10 - count}</b> نفر دیگر، لینک اشتراک هوشمند (Sub) را هم دریافت کنید!"
            )
        else:
            msg = (
                "🏆 <b>همه جوایز برای شما باز شده است:</b>\n\n"
                f"1️⃣ <b>لینک کانال اختصاصی VIP:</b>\n{VIP_INVITE_LINK}\n\n"
                f"2️⃣ <b>لینک ساب‌اسکریپشن هوشمند کاسپین:</b>\n<code>{SUB_LINK}</code>"
            )
        send_message(chat_id, msg, get_main_keyboard())

    telegram_api("answerCallbackQuery", {"callback_query_id": cb_id})

def main():
    print("ربات رفرال کاسپین آنلاین شد...")
    last_update_id = 0
    while True:
        try:
            updates = telegram_api("getUpdates", {"offset": last_update_id + 1, "timeout": 20})
            if updates and updates.get("ok"):
                for u in updates["result"]:
                    last_update_id = u["update_id"]
                    if "message" in u:
                        handle_message(u["message"])
                    elif "callback_query" in u:
                        handle_callback(u["callback_query"])
        except Exception as e:
            print(f"خطای حلقه اصلی: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
