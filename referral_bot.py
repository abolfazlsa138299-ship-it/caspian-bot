import html
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import threading
import time
import urllib.parse
import urllib.request

# تنظیمات ربات و کانال
BOT_TOKEN = "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y"
MAIN_CHANNEL = "@proxy_caspian"
VIP_LINK = "https://t.me/+kRHTDOtFljQ1NzBk"
SUB_URL = "https://raw.githubusercontent.com/abolfazlsa138299-ship-it/caspian-bot/main/sub.txt"

# آیدی تلگرام شما (مالک و مدیر کل مجموعه)
ADMIN_ID = 9224931872

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# دیتابیس ساده در حافظه برای رفرال‌ها
# {user_id: {"inviter": inviter_id, "confirmed_invites": set()}}
users_db = {}


# --- سرور وب کوچک برای زنده نگه داشتن برنامه در رندر (Render) ---
class SimpleWebServer(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Caspian Referral Bot is Running 24/7!")

    def log_message(self, format, *args):
        return  # خاموش کردن لاگ‌های اضافه وب


def start_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleWebServer)
    print(f"[*] وب‌سرور Render روی پورت {port} روشن شد.")
    server.serve_forever()


# --- ارتباط با API تلگرام ---
def tg_api(method, payload):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"ok": False, "error": str(e)}


def is_member(user_id):
    """بررسی عضویت کاربر در کانال اصلی"""
    res = tg_api(
        "getChatMember", {"chat_id": MAIN_CHANNEL, "user_id": user_id}
    )
    if res.get("ok"):
        status = res.get("result", {}).get("status", "")
        return status in ["member", "administrator", "creator"]
    return False


def get_admin_keyboard():
    """کیبورد مخصوص ادمین"""
    return json.dumps(
        {
            "keyboard": [
                [{"text": "👥 دریافت لینک دعوت"}, {"text": "📊 آمار دعوت‌های من"}],
                [{"text": "🧪 تست ساب‌اسکریپشن (مدیریت)"}],
            ],
            "resize_keyboard": True,
        }
    )


def get_user_keyboard():
    """کیبورد عادی برای کاربران"""
    return json.dumps(
        {
            "keyboard": [
                [{"text": "👥 دریافت لینک دعوت"}, {"text": "📊 آمار دعوت‌های من"}]
            ],
            "resize_keyboard": True,
        }
    )


def handle_admin_test_sub(chat_id):
    """دریافت آخرین محتوای sub.txt و ارسال آن برای ادمین جهت تست"""
    try:
        req = urllib.request.Request(SUB_URL, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore").strip()
            lines = [line.strip() for line in content.split("\n") if line.strip()]

        if not lines:
            tg_api(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": "⚠️ فایل sub.txt در حال حاضر خالی است یا در گیت‌هاب لود نشد.",
                },
            )
            return

        # گرفتن ۳ کانفیگ اول برای تست فوری
        sample_configs = lines[:3]
        formatted_cfgs = "\n\n".join(
            [f"🔹 <code>{html.escape(c)}</code>" for c in sample_configs]
        )

        msg = (
            "👑 <b>پنل دسترسی مستقیم مدیریت کاسپین</b> 👑\n\n"
            f"📊 <b>تعداد کل کانفیگ‌های فعال در ساب:</b> {len(lines)} عدد\n\n"
            "🔍 <b>۳ کانفیگ تازه‌نفس فعلی (یکبار ضربه بزنید تا کپی شود):</b>\n\n"
            f"{formatted_cfgs}\n\n"
            f"🔗 <b>لینک مستقیم ساب‌اسکریپشن:</b>\n<code>{SUB_URL}</code>"
        )

        tg_api(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": msg,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
        )
    except Exception as e:
        tg_api(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": f"❌ خطا در خواندن لینک ساب‌اسکریپشن: {e}",
            },
        )


def handle_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    user_id = msg.get("from", {}).get("id")
    text = msg.get("text", "").strip()

    if not chat_id or not user_id:
        return

    is_admin = user_id == ADMIN_ID
    reply_kb = get_admin_keyboard() if is_admin else get_user_keyboard()

    if user_id not in users_db:
        users_db[user_id] = {"inviter": None, "confirmed_invites": set()}

    # دستور استارت
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter_id = int(parts[1])
            if inviter_id != user_id and users_db[user_id]["inviter"] is None:
                users_db[user_id]["inviter"] = inviter_id

        welcome_text = (
            "سلام به مجموعه ارتباطی کاسپین خوش آمدید ⚜️\n\n"
            "با دعوت دوستانتان به کانال، جوایز پرسرعت و بدون فیلتر دریافت کنید:\n"
            "▫️ ۵ دعوت موفق ⬅️ ورود دائمی به کانال اختصاصی VIP\n"
            "▫️ ۱۰ دعوت موفق ⬅️ دریافت ساب‌اسکریپشن هوشمند کاسپین\n\n"
            "جهت شروع از دکمه‌های زیر استفاده کنید:"
        )
        tg_api(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": welcome_text,
                "reply_markup": reply_kb,
            },
        )
        return

    # دستور اختصاصی ادمین
    if is_admin and (
        text == "🧪 تست ساب‌اسکریپشن (مدیریت)" or "تست ساب" in text.lower()
    ):
        handle_admin_test_sub(chat_id)
        return

    # دریافت لینک دعوت
    if text == "👥 دریافت لینک دعوت":
        invite_link = f"https://t.me/CaspianProxyBot?start={user_id}"
        resp_msg = (
            "🔗 <b>لینک دعوت اختصاصی شما:</b>\n\n"
            f"<code>{invite_link}</code>\n\n"
            "این لینک را برای دوستان یا در گروه‌ها بفرستید. به ازای هر نفری که عضو کانال شود، امتیاز شما ثبت خواهد شد."
        )
        tg_api(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": resp_msg,
                "parse_mode": "HTML",
                "reply_markup": reply_kb,
            },
        )
        return

    # آمار دعوت‌ها و بررسی اهدا جوایز
    if text == "📊 آمار دعوت‌های من":
        # بررسی عضویت کسانی که این کاربر دعوت کرده
        confirmed = 0
        for uid, data in users_db.items():
            if data.get("inviter") == user_id:
                if is_member(uid):
                    confirmed += 1

        stats_msg = f"📊 <b>وضعیت دعوت‌های شما:</b>\n\n" f"👥 تعداد افراد دعوت‌شده و فعال: <b>{confirmed} نفر</b>\n\n"

        if is_admin:
            stats_msg += "👑 شما مدیر کل سیستم هستید و به تمام بخش‌ها دسترسی نامحدود دارید."
        elif confirmed >= 10:
            stats_msg += f"🎉 تبریک! شما به سقف ۱۰ دعوت رسیدید:\n\n🔗 لینک ساب‌اسکریپشن شما:\n<code>{SUB_URL}</code>\n\n👑 لینک کانال VIP:\n{VIP_LINK}"
        elif confirmed >= 5:
            stats_msg += f"🎁 تبریک! ۵ دعوت شما تکمیل شد:\n\n👑 لینک ورود به کانال اختصاصی VIP:\n{VIP_LINK}\n\n(با ۵ دعوت دیگر، لینک ساب‌اسکریپشن هوشمند را هم دریافت می‌کنید!)"
        else:
            stats_msg += f"برای دریافت لینک VIP هنوز به {5 - confirmed} دعوت دیگر نیاز دارید."

        tg_api(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": stats_msg,
                "parse_mode": "HTML",
                "reply_markup": reply_kb,
            },
        )
        return


def polling_loop():
    offset = 0
    print("[*] حلقه Polling ربات فعال شد.")
    while True:
        try:
            res = tg_api("getUpdates", {"offset": offset, "timeout": 20})
            if res.get("ok"):
                for update in res.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" in update:
                        handle_message(update["message"])
        except Exception as e:
            time.sleep(2)
        time.sleep(0.5)


if __name__ == "__main__":
    # اجرای وب‌سرور در پس‌زمینه برای Render
    t = threading.Thread(target=start_web_server, daemon=True)
    t.start()

    # اجرای هسته ربات
    polling_loop()
