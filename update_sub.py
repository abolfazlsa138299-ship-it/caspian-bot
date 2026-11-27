import os
import json
import urllib.request
import re
import socket
import urllib.parse
import base64
import html
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = os.environ.get("BOT_TOKEN", "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y")
VIP_CHANNEL_ID = -1005629553208  # آیدی کانال VIP شما

# سورس‌های اختصاصی VLESS Reality (تنها پروتکل فعال در ایران)
SOURCES = [
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/reality",
    "https://raw.githubusercontent.com/yebekhe/Telegram-V2ray-Configs/main/sub/reality",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/reality"
]

def decode_base64_if_needed(text):
    text = text.strip()
    try:
        decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
        if "vless://" in decoded:
            return decoded
    except Exception:
        pass
    return text

def fetch_configs():
    raw_configs = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for src in SOURCES:
        try:
            req = urllib.request.Request(src, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                decoded_content = decode_base64_if_needed(content)
                for line in decoded_content.splitlines():
                    line = line.strip()
                    # فقط و فقط VLESS (مخصوصاً Reality) - حذف کامل پروتکل‌های سوخته مثل ss
                    if line.startswith("vless://") and ("reality" in line.lower() or "security=reality" in line.lower() or "443" in line):
                        raw_configs.append(line)
        except Exception as e:
            print(f"خطا در دریافت: {e}")
    return list(set(raw_configs))

def check_config_alive(config):
    try:
        parsed = urllib.parse.urlparse(config)
        host = parsed.hostname
        port = parsed.port
        if not host or not port:
            return None

        # تست سریع سوکت
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        res = sock.connect_ex((host, int(port)))
        sock.close()

        if res == 0:
            return config
    except:
        pass
    return None

def send_vip_post(configs):
    """ارسال پست با چیدمان ۲ تایی از هر نوع (مجموعاً ۶ کانفیگ)"""
    v2_1 = html.escape(configs[0].split("#")[0] + "#⚡️ Caspian | V2Ray 1")
    v2_2 = html.escape(configs[1].split("#")[0] + "#⚡️ Caspian | V2Ray 2")

    npv_1 = html.escape(configs[2].split("#")[0] + "#⚡️ Caspian | NPV Tunnel 1")
    npv_2 = html.escape(configs[3].split("#")[0] + "#⚡️ Caspian | NPV Tunnel 2")

    dual_1 = html.escape(configs[4].split("#")[0] + "#⚡️ Caspian | دوکاره 1")
    dual_2 = html.escape(configs[5].split("#")[0] + "#⚡️ Caspian | دوکاره 2")

    caption = (
        "👑 <b>پست اختصاصی اعضای کاسپین VIP</b> 👑\n\n"
        "کانفیگ‌های پرسرعت و تست‌شده اختصاصی (VLESS Reality):\n\n"
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
        with urllib.request.urlopen(req, timeout=10) as r:
            print("پست ۶ تایی با موفقیت به کانال VIP ارسال شد!")
    except Exception as e:
        print(f"خطا در ارسال به کانال VIP: {e}")

def main():
    print("شروع استخراج کانفیگ‌های ضدفیلتر VLESS Reality...")
    all_configs = fetch_configs()
    print(f"تعداد {len(all_configs)} کانفیگ Reality پیدا شد. در حال پینگ گرفتن...")

    alive_configs = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(check_config_alive, all_configs[:100])
        for r in results:
            if r:
                alive_configs.append(r)
                if len(alive_configs) >= 15:
                    break

    if alive_configs:
        # آپدیت فایل ساب‌اسکریپشن
        final_labeled = []
        for i, cfg in enumerate(alive_configs):
            base_url = cfg.split("#")[0]
            tag = f"⚡️ Caspian Reality #{i+1}"
            final_labeled.append(f"{base_url}#{urllib.parse.quote(tag)}")

        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_labeled))
        print("فایل sub.txt آپدیت شد.")

        # ارسال پست ۶ تایی به کانال VIP
        if len(alive_configs) >= 6:
            send_vip_post(alive_configs[:6])
        elif len(alive_configs) >= 3:
            # اگر کمتر از ۶ تا بود باز هم دوتایی پرش کن تا پست ناقص نمونه
            send_vip_post((alive_configs * 2)[:6])

if __name__ == "__main__":
    main()
