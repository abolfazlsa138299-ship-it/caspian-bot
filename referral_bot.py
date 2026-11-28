import os
import json
import logging
import threading
import urllib.request
import base64
from flask import Flask, Response
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN", "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y")
VIP_CHANNEL_LINK = "https://t.me/+kRHTDOtFljQ1NzBk"
ADMIN_ID = 9224931872
DATA_FILE = "data.json"
SUB_DIRECT_URL = "https://caspian-bot-c0b6.onrender.com/sub"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)
data_lock = threading.Lock()

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Save error: {e}")

def get_user_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔗 دریافت لینک دعوت اختصاصی", callback_data="get_link"),
        types.InlineKeyboardButton("📊 آمار دعوت و جوایز من", callback_data="my_stats"),
        types.InlineKeyboardButton("🎁 صندوق دریافت جوایز", callback_data="claim_rewards"),
        types.InlineKeyboardButton("⚡️ عضویت در کانال اصلی کاسپین", url="https://t.me/proxy_caspian")
    )
    return markup

def get_admin_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🏆 آمار دریافت‌کنندگان جوایز", "👥 افراد در حال انجام روتین")
    markup.row("🧪 تست ساب‌اسکریپشن (مدیریت)")
    return markup

@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "کاربر گرامی"

    with data_lock:
        data = load_data()
        user_str = str(user_id)
        if user_str not in data["users"]:
            data["users"][user_str] = {
                "invites": 0,
                "invited_by": None,
                "first_name": first_name,
                "username": username,
                "claimed_5": False,
                "claimed_10": False
            }
            args = message.text.split()
            if len(args) > 1 and args[1].isdigit():
                ref_id = args[1]
                if ref_id != user_str and ref_id in data["users"]:
                    data["users"][user_str]["invited_by"] = ref_id
                    data["users"][ref_id]["invites"] += 1
                    save_data(data)
                    try:
                        count = data["users"][ref_id]["invites"]
                        bot.send_message(
                            int(ref_id),
                            f"🎉 <b>یک عضو جدید با لینک شما وارد شد!</b>\n\n"
                            f"👤 کاربر: <b>{first_name}</b>\n"
                            f"📊 مجموع دعوت‌های شما: <b>{count} نفر</b>\n\n"
                            f"⚡️ <i>با تشکر از همراهی شما با مجموعه کاسپین.</i>"
                        )
                        check_rewards(int(ref_id), count, data)
                    except Exception:
                        pass
        save_data(data)

    welcome_text = (
        "به ربات رسمی جوایز پروکسی کاسپین خوش آمدید! ⚡️\n\n"
        "🎁 <b>طرح دعوت و دریافت فیلترشکن رایگان (بدون قرعه‌کشی):</b>\n"
        "🔹 با دعوت ۵ نفر ⬅️ عضویت در کانال اختصاصی VIP کاسپین\n"
        "🔹 با دعوت ۱۰ نفر ⬅️ دریافت لینک اشتراک هوشمند (Sub) با آپدیت خودکار\n\n"
        "🚶‍♂️ <b>از دکمه‌های زیر برای دریافت لینک دعوت و مشاهده آمار خود استفاده کنید:</b>"
    )

    if user_id == ADMIN_ID:
        bot.send_message(user_id, "👑 <b>پنل ویژه مدیریت کاسپین فعال شد:</b>", reply_markup=get_admin_reply_keyboard())
    bot.send_message(user_id, welcome_text, reply_markup=get_user_inline_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    with data_lock:
        data = load_data()
        invites = data["users"].get(str(user_id), {}).get("invites", 0)

    bot.answer_callback_query(call.id)

    if call.data == "get_link":
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start={user_id}"
        msg = (
            f"⚜️ <b>لینک اختصاصی شما:</b>\n\n<code>{link}</code>\n\n"
            f"📢 <b>متن دعوت:</b>\nکانفیگ پرسرعت و اختصاصی، هدیه همیشگی مجموعه کاسپین ⚜️\n"
            f"بدون خرید VPN، سرورهای رایگان و پرسرعت دریافت کن:\n{link}"
        )
        bot.send_message(user_id, msg)

    elif call.data == "my_stats":
        msg = f"📊 <b>وضعیت حساب شما:</b>\n\n👥 دعوت‌های ثبت‌شده: <b>{invites} نفر</b>\n"
        if invites >= 10:
            msg += "▫️ کانال VIP: فعال ✅\n▫️ ساب‌اسکریپشن هوشمند: فعال ✅"
        elif invites >= 5:
            msg += f"▫️ کانال VIP: فعال ✅\n▫️ ساب‌اسکریپشن هوشمند: {10 - invites} دعوت باقی‌مانده ⏳"
        else:
            msg += f"▫️ کانال VIP: {5 - invites} دعوت باقی‌مانده ⏳\n▫️ ساب‌اسکریپشن: {10 - invites} دعوت باقی‌مانده ⏳"
        bot.send_message(user_id, msg)

    elif call.data == "claim_rewards":
        if invites < 5:
            bot.send_message(user_id, f"🎁 برای دریافت کانال VIP به <b>{5 - invites} دعوت دیگر</b> نیاز دارید.")
        elif 5 <= invites < 10:
            bot.send_message(user_id, f"🎁 <b>جایزه سطح ۱:</b>\n🔗 ورود به کانال VIP:\n{VIP_CHANNEL_LINK}\n\n⏳ {10 - invites} دعوت تا دریافت ساب هوشمند.")
        else:
            bot.send_message(user_id, f"🎁 <b>جوایز شما:</b>\n\n✅ ۱. کانال VIP:\n{VIP_CHANNEL_LINK}\n\n✅ ۲. لینک ساب هوشمند کاسپین:\n<code>{SUB_DIRECT_URL}</code>")

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID and msg.text == "🏆 آمار دریافت‌کنندگان جوایز")
def admin_claimers(message):
    data = load_data()
    sub_w = [f"▫️ {u.get('first_name')} (<code>{k}</code>) ⬅️ {u.get('invites')} دعوت" for k, u in data.get("users", {}).items() if u.get("invites", 0) >= 10]
    vip_w = [f"▫️ {u.get('first_name')} (<code>{k}</code>) ⬅️ {u.get('invites')} دعوت" for k, u in data.get("users", {}).items() if 5 <= u.get("invites", 0) < 10]
    msg = f"👑 <b>گزارش برندگان جوایز کاسپین:</b>\n\n🌟 <b>ساب‌اسکریپشن (۱۰+ دعوت): {len(sub_w)} نفر</b>\n" + "\n".join(sub_w[:15]) + f"\n\n🎖 <b>کانال VIP (۵-۹ دعوت): {len(vip_w)} نفر</b>\n" + "\n".join(vip_w[:15])
    bot.send_message(ADMIN_ID, msg)

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID and msg.text == "👥 افراد در حال انجام روتین")
def admin_routine(message):
    data = load_data()
    users = data.get("users", {})
    s1 = sum(1 for u in users.values() if 1 <= u.get("invites", 0) <= 4)
    s2 = sum(1 for u in users.values() if 5 <= u.get("invites", 0) <= 9)
    s3 = sum(1 for u in users.values() if u.get("invites", 0) >= 10)
    msg = f"📊 <b>آمار زنجیره روتین:</b>\n\n👥 کل کاربران: {len(users)} نفر\n▫️ مرحله VIP (۱ تا ۴): {s1} نفر\n▫️ مرحله ساب (۵ تا ۹): {s2} نفر\n▫️ تکمیل‌شده (۱۰+): {s3} نفر"
    bot.send_message(ADMIN_ID, msg)

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID and msg.text == "🧪 تست ساب‌اسکریپشن (مدیریت)")
def admin_test_sub(message):
    bot.send_message(ADMIN_ID, f"👑 <b>لینک استاندارد و ضد فیلتر ساب کاسپین:</b>\n\n<code>{SUB_DIRECT_URL}</code>\n\nاین لینک را در NPV یا V2Ray وارد کنید تا بدون فیلترشکن کانفیگ‌ها لود شوند.")

def check_rewards(user_id, count, data):
    u = str(user_id)
    if count >= 5 and not data["users"][u].get("claimed_5", False):
        data["users"][u]["claimed_5"] = True
        bot.send_message(user_id, f"🎉 <b>تبریک! شما به ۵ دعوت رسیدید.</b>\n\n🔗 ورود به کانال VIP کاسپین:\n{VIP_CHANNEL_LINK}")
    if count >= 10 and not data["users"][u].get("claimed_10", False):
        data["users"][u]["claimed_10"] = True
        bot.send_message(user_id, f"👑 <b>تبریک! شما به ۱۰ دعوت رسیدید.</b>\n\n⚡️ لینک ساب‌اسکریپشن هوشمند شما:\n<code>{SUB_DIRECT_URL}</code>")

# سرویس‌دهنده ساب‌اسکریپشن مستقیم Base64 برای NPV Tunnel و V2Ray
@app.route("/sub")
def serve_sub():
    try:
        url = "https://raw.githubusercontent.com/abolfazlsa138299-ship-it/caspian-bot/main/sub.txt"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8").strip()
        b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        return Response(b64_content, mimetype="text/plain; charset=utf-8")
    except Exception as e:
        return f"Error: {e}", 500

@app.route("/")
def index():
    return "Caspian Sub Server is Online ⚡️"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling(skip_pending=True)
