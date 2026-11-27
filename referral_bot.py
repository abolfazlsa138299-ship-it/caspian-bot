import os
import json
import logging
import threading
import urllib.parse
from flask import Flask, request, render_template_string
import telebot
from telebot import types

# --- Configuration ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y")
CHANNEL_ID = "@proxy_caspian"
VIP_CHANNEL_LINK = "https://t.me/+kRHTDOtFljQ1NzBk"
MASKED_SUB_LINK = "https://tinyurl.com/caspian-vip-sub"
ADMIN_ID = 9224931872
DATA_FILE = "data.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

# --- Data Management ---
data_lock = threading.Lock()

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {DATA_FILE}: {e}")
        return {"users": {}}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error saving {DATA_FILE}: {e}")

def check_channel_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["creator", "administrator", "member"]
    except Exception as e:
        logging.warning(f"Membership check failed for {user_id}: {e}")
        return False

# --- Keyboards ---
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

# --- Handlers ---
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "کاربر گرامی"

    with data_lock:
        data = load_data()
        user_str = str(user_id)
        is_new = user_str not in data["users"]

        if is_new:
            data["users"][user_str] = {
                "invites": 0,
                "invited_by": None,
                "first_name": first_name,
                "username": username,
                "claimed_5": False,
                "claimed_10": False
            }

            # Handle Referral Parameter
            args = message.text.split()
            if len(args) > 1 and args[1].isdigit():
                referrer_id = args[1]
                if referrer_id != user_str and referrer_id in data["users"]:
                    data["users"][user_str]["invited_by"] = referrer_id
                    data["users"][referrer_id]["invites"] += 1
                    ref_count = data["users"][referrer_id]["invites"]
                    save_data(data)

                    try:
                        bot.send_message(
                            int(referrer_id),
                            f"🎉 <b>یک عضو جدید با لینک اختصاصی شما به ربات پیوست!</b>\n\n"
                            f"👤 کاربر: <b>{first_name}</b>\n"
                            f"📊 مجموع دعوت‌های معتبر شما: <b>{ref_count} نفر</b>\n\n"
                            f"⚡️ <i>با تشکر فراوان از همراهی و حمایت شما از مجموعه کاسپین.</i>"
                        )
                        check_and_notify_rewards(int(referrer_id), ref_count, data)
                    except Exception as e:
                        logging.warning(f"Could not notify referrer {referrer_id}: {e}")

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
    else:
        bot.send_message(user_id, welcome_text, reply_markup=get_user_inline_keyboard())

# --- Callback Query Handler (For User Menu in Image 2) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    user_str = str(user_id)

    with data_lock:
        data = load_data()
        user_info = data["users"].get(user_str, {"invites": 0})
        invites = user_info.get("invites", 0)

    bot.answer_callback_query(call.id)

    if call.data == "get_link":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        share_text = (
            f"⚜️ <b>لینک دعوت اختصاصی شما:</b>\n\n"
            f"<code>{ref_link}</code>\n\n"
            f"📢 <b>متن آماده جهت فوروارد برای دوستان:</b>\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"کانفیگ پرسرعت و اختصاصی، هدیه همیشگی مجموعه کاسپین ⚜️\n\n"
            f"دیگه نیازی به خرید فیلترشکن نداری! وارد ربات کاسپین شو و سرورهای رایگان و پرسرعت دریافت کن:\n"
            f"👇👇\n"
            f"{ref_link}"
        )
        bot.send_message(user_id, share_text)

    elif call.data == "my_stats":
        stats_text = (
            f"📊 <b>گزارش آمار و وضعیت فعالیت شما:</b>\n\n"
            f"👤 شناسه کاربری: <code>{user_id}</code>\n"
            f"👥 تعداد کل دعوت‌های ثبت‌شده: <b>{invites} نفر</b>\n\n"
            f"🎯 <b>وضعیت جوایز:</b>\n"
        )
        if invites >= 10:
            stats_text += "▫️ کانال اختصاصی VIP: <b>فعال و دریافت‌شده ✅</b>\n"
            stats_text += "▫️ ساب‌اسکریپشن هوشمند: <b>فعال و دریافت‌شده ✅</b>\n\n"
            stats_text += "⚡️ <i>صمیمانه از همراهی بی‌نظیر شما با مجموعه کاسپین سپاسگزاریم.</i>"
        elif invites >= 5:
            stats_text += "▫️ کانال اختصاصی VIP: <b>فعال و دریافت‌شده ✅</b>\n"
            stats_text += f"▫️ ساب‌اسکریپشن هوشمند: <b>{10 - invites} دعوت باقی‌مانده ⏳</b>\n\n"
            stats_text += "💪 <i>فقط چند دعوت دیگر تا دریافت لینک اشتراک خودکار فاصله دارید!</i>"
        else:
            stats_text += f"▫️ کانال اختصاصی VIP: <b>{5 - invites} دعوت باقی‌مانده ⏳</b>\n"
            stats_text += f"▫️ ساب‌اسکریپشن هوشمند: <b>{10 - invites} دعوت باقی‌مانده ⏳</b>"

        bot.send_message(user_id, stats_text)

    elif call.data == "claim_rewards":
        if invites < 5:
            bot.send_message(
                user_id,
                f"🎁 <b>صندوق جوایز شما:</b>\n\n"
                f"شما تاکنون <b>{invites} نفر</b> را دعوت کرده‌اید.\n"
                f"برای بازگشایی «کانال اختصاصی VIP» به <b>{5 - invites} دعوت دیگر</b> نیاز دارید.\n\n"
                f"با ارسال لینک دعوت به دوستانتان، جوایز به صورت کاملاً خودکار برای شما ارسال خواهند شد. ⚡️"
            )
        elif 5 <= invites < 10:
            bot.send_message(
                user_id,
                f"🎁 <b>صندوق جوایز فعال شما:</b>\n\n"
                f"✅ <b>جایزه سطح ۱ (عضویت در کانال اختصاصی VIP):</b>\n"
                f"🔗 لینک ورود مستقیم: {VIP_CHANNEL_LINK}\n\n"
                f"⏳ <b>جایزه سطح ۲ (ساب‌اسکریپشن هوشمند):</b>\n"
                f"تنها <b>{10 - invites} دعوت دیگر</b> تا دریافت لینک ساب اختصاصی باقی‌مانده است."
            )
        else:
            bot.send_message(
                user_id,
                f"🎁 <b>صندوق جوایز کامل شما:</b>\n\n"
                f"✅ <b>۱. لینک ورود به کانال اختصاصی VIP:</b>\n"
                f"🔗 {VIP_CHANNEL_LINK}\n\n"
                f"✅ <b>۲. لینک ساب‌اسکریپشن هوشمند کاسپین:</b>\n"
                f"<code>{MASKED_SUB_LINK}</code>\n\n"
                f"🌹 <i>با سپاس بی‌کران از اعتماد و حمایت همیشگی شما از مجموعه کاسپین.</i>"
            )

# --- Admin Panel Text Handlers ---
@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID and msg.text == "🏆 آمار دریافت‌کنندگان جوایز")
def admin_claimers_stats(message):
    with data_lock:
        data = load_data()

    users = data.get("users", {})
    winners_sub = []
    winners_vip = []

    for uid, udata in users.items():
        inv = udata.get("invites", 0)
        uname = udata.get("first_name", "کاربر")
        if inv >= 10:
            winners_sub.append(f"▫️ {uname} (<code>{uid}</code>) ⬅️ <b>{inv} دعوت</b>")
        elif inv >= 5:
            winners_vip.append(f"▫️ {uname} (<code>{uid}</code>) ⬅️ <b>{inv} دعوت</b>")

    report = "👑 <b>گزارش کاربران دریافت‌کننده جوایز (کاسپین):</b>\n\n"
    report += f"🌟 <b>برندگان ساب‌اسکریپشن (۱۰ دعوت و بالاتر): {len(winners_sub)} نفر</b>\n"
    if winners_sub:
        report += "\n".join(winners_sub[:15]) + ("\n..." if len(winners_sub) > 15 else "") + "\n\n"
    else:
        report += "<i>هنوز کاربری به سطح ۱۰ دعوت نرسیده است.</i>\n\n"

    report += f"🎖 <b>برندگان کانال VIP (۵ تا ۹ دعوت): {len(winners_vip)} نفر</b>\n"
    if winners_vip:
        report += "\n".join(winners_vip[:15]) + ("\n..." if len(winners_vip) > 15 else "")
    else:
        report += "<i>کاربری در این رده ثبت نشده است.</i>"

    bot.send_message(ADMIN_ID, report)

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID and msg.text == "👥 افراد در حال انجام روتین")
def admin_in_progress_stats(message):
    with data_lock:
        data = load_data()

    users = data.get("users", {})
    total_users = len(users)
    stage_1_to_4 = 0
    stage_5_to_9 = 0
    completed_10 = 0
    zero_invites = 0

    for uid, udata in users.items():
        inv = udata.get("invites", 0)
        if inv == 0:
            zero_invites += 1
        elif 1 <= inv <= 4:
            stage_1_to_4 += 1
        elif 5 <= inv <= 9:
            stage_5_to_9 += 1
        else:
            completed_10 += 1

    report = (
        "📊 <b>آمار تفکیکی کاربران در حال انجام روتین دعوت:</b>\n\n"
        f"👥 کل کاربران ثبت‌شده در ربات: <b>{total_users} نفر</b>\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"⏳ <b>در حال تلاش برای کانال VIP (۱ تا ۴ دعوت):</b> {stage_1_to_4} نفر\n"
        f"⏳ <b>در حال تلاش برای ساب‌اسکریپشن (۵ تا ۹ دعوت):</b> {stage_5_to_9} نفر\n"
        f"🏆 <b>تکمیل‌کنندگان کامل روتین (۱۰+ دعوت):</b> {completed_10} نفر\n"
        f"💤 <b>کاربران بدون دعوت (۰ دعوت):</b> {zero_invites} نفر\n\n"
        f"⚡️ <i>مجموع کل کاربران فعال در زنجیره دعوت: <b>{stage_1_to_4 + stage_5_to_9 + completed_10} نفر</b></i>"
    )
    bot.send_message(ADMIN_ID, report)

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID and msg.text == "🧪 تست ساب‌اسکریپشن (مدیریت)")
def admin_test_subscription(message):
    try:
        import urllib.request
        sub_url = "https://raw.githubusercontent.com/abolfazlsa138299-ship-it/caspian-bot/main/sub.txt"
        req = urllib.request.Request(sub_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8").strip()
            configs = [c.strip() for c in content.splitlines() if c.strip()]
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ خطا در خواندن ساب‌اسکریپشن مخزن: {e}")
        return

    configs_text = "\n\n".join([f"<code>{c}</code>" for c in configs[:7]])
    test_msg = (
        "👑 <b>تست محتوای ساب‌اسکریپشن اختصاصی کاسپین (مخصوص مدیریت)</b> 👑\n\n"
        f"🔗 <b>لینک مستقیم ساب‌اسکریپشن:</b>\n<code>{MASKED_SUB_LINK}</code>\n\n"
        f"📋 <b>کانفیگ‌های فعال درون ساب (تعداد {len(configs)} عدد):</b>\n\n"
        f"{configs_text}"
    )
    bot.send_message(ADMIN_ID, test_msg)

def check_and_notify_rewards(user_id, count, data):
    user_str = str(user_id)
    if count >= 5 and not data["users"][user_str].get("claimed_5", False):
        data["users"][user_str]["claimed_5"] = True
        msg = (
            "🎉 <b>تبریک فراوان! شما به حد نصاب ۵ دعوت رسیدید.</b>\n\n"
            "به پاس قدردانی از همراهی ارزشمند شما، لینک ورود به <b>کانال اختصاصی VIP کاسپین</b> تقدیم حضورتان می‌گردد:\n\n"
            f"🔗 <b>لینک ورود به کانال اختصاصی:</b>\n{VIP_CHANNEL_LINK}\n\n"
            "✨ <i>با دعوت ۵ نفر دیگر (مجموعاً ۱۰ نفر)، لینک ساب‌اسکریپشن هوشمند را نیز دریافت خواهید کرد.</i>"
        )
        bot.send_message(user_id, msg)

    if count >= 10 and not data["users"][user_str].get("claimed_10", False):
        data["users"][user_str]["claimed_10"] = True
        msg = (
            "👑 <b>تبریک صمیمانه! شما موفق به ثبت ۱۰ دعوت موفق شدید.</b>\n\n"
            "مجموعه کاسپین مراتب سپاس و قدردانی صمیمانه خود را بابت حمایت شما اعلام می‌دارد.\n\n"
            "⚡️ <b>لینک ساب‌اسکریپشن هوشمند اختصاصی شما (با آپدیت خودکار):</b>\n"
            f"<code>{MASKED_SUB_LINK}</code>\n\n"
            "💡 <i>این لینک را مستقیماً در نرم‌افزارهای V2RayNG یا NPV Tunnel وارد نمایید تا سرورها همواره متصل و بدون قطعی باقی بمانند.</i>"
        )
        bot.send_message(user_id, msg)

# --- Web Server for UptimeRobot & Redirects ---
REDIRECT_HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پروکسی کاسپین | اتصال سریع</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }
        .card { background: #1e293b; padding: 2.5rem; border-radius: 1.25rem; box-shadow: 0 10px 25px rgba(0,0,0,0.5); max-width: 90%; width: 360px; }
        .btn { display: inline-block; background: #38bdf8; color: #0f172a; font-weight: bold; padding: 0.85rem 1.75rem; border-radius: 0.75rem; text-decoration: none; margin-top: 1.5rem; font-size: 1.1rem; }
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <div class="card">
        <h2>⚜️ مجموعه پروکسی کاسپین</h2>
        <p class="pulse">در حال انتقال مستقیم به نرم‌افزار...</p>
        <p style="font-size: 0.85rem; color: #94a3b8;">در صورت عدم باز شدن خودکار، روی دکمه زیر ضربه بزنید:</p>
        <a href="{{ target_url }}" class="btn">🚀 اتصال به فیلترشکن</a>
    </div>
    <script>
        setTimeout(function() {
            window.location.href = "{{ target_url | safe }}";
        }, 300);
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return "Caspian Referral Bot & Redirect Service is Online ⚡️"

@app.route("/health")
def health():
    return "OK", 200

@app.route("/c")
def redirect_to_config():
    config_url = request.args.get("url", "")
    if not config_url:
        return "URL is missing", 400
    decoded_url = urllib.parse.unquote(config_url)
    return render_template_string(REDIRECT_HTML, target_url=decoded_url)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logging.info("Starting Caspian Referral Bot polling...")
    bot.infinity_polling(skip_pending=True)
