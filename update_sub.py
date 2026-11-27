import os
import json
import urllib.request
import re
import socket
import urllib.parse
import html
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y"
VIP_CHANNEL_ID = -1005629553208

# کانال‌های مرجع تلگرام که لحظه‌ای کانفیگ‌های سالم VLESS Reality می‌گذارند (هرگز ۴۰۴ نمی‌شوند)
TG_CHANNELS = [
    "v2rayng_org",
    "V2rayNG_VPNN",
    "Outline_Vpn",
    "v2ray_configs_pool",
    "FreakConfig"
]

def fetch_configs_from_telegram(channel):
    url = f"https://t.me/s/{channel}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    configs = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            # استخراج تمام کانفیگ‌های vless
            found = re.findall(r'(vless://[^\s<>"\'`]+)', content)
            for c in reversed(found):
                clean = html.unescape(c).replace("&amp;", "&")
                if clean not in configs:
                    configs.append(clean)
    except Exception as e:
        print(f"Error fetching from @{channel}: {e}")
    return configs

def check_alive(config):
    try:
        parsed = urllib.parse.urlparse(config)
        host = parsed.hostname
        port = parsed.port
        if not host or not port:
            return None

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.2)
        res = sock.connect_ex((host, int(port)))
        sock.close()

        if res == 0:
            return config
    except:
        pass
    return None

def send_vip_post(configs):
    v2_1 = html.escape(configs[0].split("#")[0] + "#⚡️ Caspian | V2Ray 1")
    v2_2 = html.escape(configs[1].split("#")[0] + "#⚡️ Caspian | V2Ray 2")

    npv_1 = html.escape(configs[2].split("#")[0] + "#⚡️ Caspian | NPV Tunnel 1")
    npv_2 = html.escape(configs[3].split("#")[0] + "#⚡️ Caspian | NPV Tunnel 2")

    dual_1 = html.escape(configs[4].split("#")[0] + "#⚡️ Caspian | دوکاره 1")
    dual_2 = html.escape(configs[5].split("#")[0] + "#⚡️ Caspian | دوکاره 2")

    caption = (
        "👑 <b>پست اختصاصی اعضای کاسپین VIP</b> 👑\n\n"
        "کانفیگ‌های پرسرعت و تست‌شده اختصاصی:\n\n"
        "🔹 <b>کانفیگ‌های مخصوص V2Ray:</b>\n"
        f"1️⃣ <code>{v2_1}</code>\n\n"
        f"2️⃣ <code>{v2_2}</code>\n\n"
        "🔹 <b>کانفیگ‌های مخصوص NPV Tunnel:</b>\n"
        f"1️⃣ <code>{npv_1}</code>\n\n"
        f"2️⃣ <code>{npv_2}</code>\n\n"
        "🔹 <b>کانفیگ‌های دوکاره (پرسرعت):</b>\n"
        f"1️⃣ <code>{dual_1}</code>\n\n"
        f"2️⃣ <code>{dual_2}</code>\n\n"
        "📶 <b>مناسب برای:</b> همراه اول، ایرانسل، رایتل و وای‌فای 📊\n"
        "💡 <b>راهنما:</b> فقط کافیه روی هر کانفیگ یکبار ضربه بزنید تا خودکار کپی بشه\n"
        "و داخل برنامه اضافه کنید."
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": VIP_CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            print("پست ۶ تایی اختصاصی با موفقیت به کانال VIP ارسال شد!")
    except Exception as e:
        print(f"خطا در ارسال به کانال تلگرام: {e}")

def main():
    print("شروع استخراج کانفیگ‌های تازه از کانال‌های تلگرام...")
    pool = []
    for ch in TG_CHANNELS:
        cfgs = fetch_configs_from_telegram(ch)
        pool.extend(cfgs)

    print(f"تعداد {len(pool)} کانفیگ تازه دریافت شد. در حال فیلتر بهترین‌ها...")

    alive_configs = []
    with ThreadPoolExecutor(max_workers=25) as executor:
        results = executor.map(check_alive, pool[:80])
        for r in results:
            if r and r not in alive_configs:
                alive_configs.append(r)
                if len(alive_configs) >= 15:
                    break

    # اگر به هر دلیلی تست سوکت تعداد کمی داد، از تازه‌ترین کانفیگ‌های خام پر کن تا پست متوقف نشود
    if len(alive_configs) < 6:
        for c in pool:
            if c not in alive_configs:
                alive_configs.append(c)
                if len(alive_configs) >= 6:
                    break

    if alive_configs:
        # ۱. ذخیره فایل ساب‌اسکریپشن
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(alive_configs[:15]))
        print("فایل sub.txt آپدیت شد.")

        # ۲. ارسال پست ۶ تایی به کانال VIP
        send_vip_post(alive_configs[:6])
    else:
        print("هیچ کانفیگی یافت نشد.")

if __name__ == "__main__":
    main()
