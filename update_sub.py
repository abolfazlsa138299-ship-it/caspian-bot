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
VIP_CHANNEL_ID = -1005629553208  # آیدی اختصاصی کانال VIP شما

# سورس‌های معتبر کانفیگ
SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/base64/mix",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt"
]

def decode_base64_if_needed(text):
    text = text.strip()
    try:
        decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
        if any(proto in decoded for proto in ["vless://", "vmess://", "trojan://", "ss://"]):
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
                    if line.startswith(("vless://", "vmess://", "trojan://", "ss://")):
                        raw_configs.append(line)
        except Exception as e:
            print(f"خطا در دریافت سورس {src}: {e}")
    return list(set(raw_configs))

def check_config_alive(config):
    try:
        parsed = urllib.parse.urlparse(config)
        host = parsed.hostname
        port = parsed.port
        if not host or not port:
            return None

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.9)
        res = sock.connect_ex((host, int(port)))
        sock.close()

        if res == 0:
            return config
    except:
        pass
    return None

def send_vip_post(cfg1, cfg2, cfg3):
    """ارسال پست دقیقا مطابق با قالب درخواستی شما"""
    # تمیزکاری کانفیگ‌ها و برچسب شیک
    c1 = html.escape(cfg1.split("#")[0] + "#⚡️ Caspian | V2Ray")
    c2 = html.escape(cfg2.split("#")[0] + "#⚡️ Caspian | NPV Tunnel")
    c3 = html.escape(cfg3.split("#")[0] + "#⚡️ Caspian | دوکاره (V2Ray + NPV)")

    caption = (
        "👑 <b>کاسپین VIP پست اختصاصی اعضای</b> 👑\n\n"
        ":کانفیگ‌های پرسرعت و تست‌شده اختصاصی\n\n"
        "🔹 <b>کانفیگ اول (مخصوص V2Ray):</b>\n"
        f"<code>{c1}</code>\n\n"
        "🔹 <b>کانفیگ دوم (مخصوص NPV Tunnel):</b>\n"
        f"<code>{c2}</code>\n\n"
        "🔹 <b>کانفیگ سوم (دوکاره - پرسرعت):</b>\n"
        f"<code>{c3}</code>\n\n"
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
            print("پست اختصاصی با موفقیت به کانال VIP ارسال شد!")
    except Exception as e:
        print(f"خطا در ارسال به کانال VIP: {e}")

def main():
    print("شروع تست و استخراج کانفیگ‌های تازه...")
    all_configs = fetch_configs()
    alive_configs = []
    with ThreadPoolExecutor(max_workers=25) as executor:
        results = executor.map(check_config_alive, all_configs[:120])
        for r in results:
            if r:
                alive_configs.append(r)
                if len(alive_configs) >= 15:
                    break

    if alive_configs:
        # ۱. ذخیره ۱۵ کانفیگ در ساب‌اسکریپشن
        final_labeled = []
        for i, cfg in enumerate(alive_configs):
            base_url = cfg.split("#")[0]
            tag = f"⚡️ Caspian #{i+1}"
            final_labeled.append(f"{base_url}#{urllib.parse.quote(tag)}")

        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_labeled))
        print("فایل sub.txt آپدیت شد.")

        # ۲. ارسال پست ۳ تایی به کانال VIP با همان ظاهر زیبا
        if len(alive_configs) >= 3:
            send_vip_post(alive_configs[0], alive_configs[1], alive_configs[2])

if __name__ == "__main__":
    main()
