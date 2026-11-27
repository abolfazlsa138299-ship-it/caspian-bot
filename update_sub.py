import base64
import html
import json
import os
import re
import socket
import time
import urllib.parse
import urllib.request

BOT_TOKEN = "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y"
VIP_CHANNEL_ID = "-1005629553208"

# ۷ کانال اصلی و مرجع تلگرام که با هم تحلیل و اسکن می‌شوند
ALL_TARGET_CHANNELS = [
    "https://t.me/s/P500Y",          # کانال ارسالی شما
    "https://t.me/s/Hope_Net",
    "https://t.me/s/v2rayngvpn",
    "https://t.me/s/v2ray_free_conf",
    "https://t.me/s/customv2ray",
    "https://t.me/s/Freetech2024",
    "https://t.me/s/PrivateVPNs",
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def parse_host_port(url_str: str):
    """استخراج هاست و پورت کانفیگ‌های VLESS و VMess و Trojan"""
    try:
        clean = url_str.strip()
        if clean.startswith("vmess://"):
            b64 = clean[8:].split("#")[0].strip()
            pad = 4 - (len(b64) % 4)
            if pad != 4:
                b64 += "=" * pad
            decoded = base64.b64decode(b64).decode("utf-8", errors="ignore")
            d = json.loads(decoded)
            return d.get("add"), int(d.get("port", 443))
        
        parsed = urllib.parse.urlsplit(clean)
        return parsed.hostname, int(parsed.port or 443)
    except Exception:
        return None, None


def test_latency(host: str, port: int, timeout: float = 1.3) -> float:
    """تست زنده بودن و محاسبه تاخیر زمانی پینگ سوکت"""
    if not host or not port:
        return 9999.0
    try:
        start = time.time()
        with socket.create_connection((host, port), timeout=timeout):
            return round((time.time() - start) * 1000, 1)
    except Exception:
        return 9999.0


def fetch_channel_configs(channel_url: str) -> list:
    """اسکرپ زنده آخرین پست‌های کانال تلگرامی"""
    try:
        req = urllib.request.Request(channel_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            found = re.findall(r"(?:vless|vmess|trojan)://[^\s<>\"\'\n\r]+", content)
            return found[-15:] if len(found) > 15 else found
    except Exception as e:
        print(f"[-] خطا در منبع {channel_url}: {e}")
        return []


def clean_and_rename_config(config_str: str, index: int, label: str) -> str:
    """تغییر نام شکیل کانفیگ به برند کاسپین"""
    clean = config_str.strip()
    tag_name = f"Caspian-{label}-{index} ⚡ @proxy_caspian"
    
    if clean.startswith("vmess://"):
        try:
            b64 = clean[8:].split("#")[0].strip()
            pad = 4 - (len(b64) % 4)
            if pad != 4:
                b64 += "=" * pad
            decoded = base64.b64decode(b64).decode("utf-8", errors="ignore")
            d = json.loads(decoded)
            d["ps"] = tag_name
            new_b64 = base64.b64encode(json.dumps(d).encode("utf-8")).decode("utf-8")
            return f"vmess://{new_b64}"
        except Exception:
            return clean

    raw_config = clean.split("#")[0].strip()
    tag = urllib.parse.quote(tag_name)
    return f"{raw_config}#{tag}"


def send_telegram_vip_message(caption: str):
    """ارسال پست شکیل به کانال VIP"""
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": VIP_CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print("[+] پست با موفقیت به کانال VIP ارسال شد.")
    except Exception as e:
        print(f"[-] خطا در ارسال پیام به کانال VIP: {e}")


def main():
    print("[*] در حال اسکن همزمان هر ۷ کانال تلگرامی...")
    all_extracted = []

    for chan in ALL_TARGET_CHANNELS:
        cfgs = fetch_channel_configs(chan)
        print(f"[+] از {chan} تعداد {len(cfgs)} کانفیگ جدید استخراج شد.")
        all_extracted.extend(cfgs)

    # ادغام همه کانفیگ‌ها در یک کاسه و حذف تکراری‌ها
    unique_pool = list(dict.fromkeys(all_extracted))
    print(f"[*] کل کانفیگ‌های یکتای استخراج‌شده از هر ۷ کانال: {len(unique_pool)}")

    print("[*] در حال تحلیل پینگ و سنجش کیفیت سرورها...")
    tested_pool = []

    for cfg in unique_pool:
        host, port = parse_host_port(cfg)
        if host and port:
            ping = test_latency(host, port, timeout=1.3)
            if ping < 9999.0:
                tested_pool.append((ping, cfg))
                print(f"  [✓ پینگ {ping}ms] {host}:{port}")
                if len(tested_pool) >= 35:
                    break

    # مرتب‌سازی بر اساس کمترین تاخیر و بالاترین سرعت
    tested_pool.sort(key=lambda x: x[0])
    sorted_configs = [item[1] for item in tested_pool]

    if len(sorted_configs) < 6:
        for c in unique_pool:
            if c not in sorted_configs:
                sorted_configs.append(c)
            if len(sorted_configs) >= 6:
                break

    # انتخاب کم‌پینگ‌ترین‌ها برای توربو
    turbo1 = clean_and_rename_config(sorted_configs[0], 1, "Turbo")
    turbo2 = clean_and_rename_config(sorted_configs[1], 2, "Turbo")

    # انتخاب کانفیگ‌های بعدی برای همراه اول
    mci1 = clean_and_rename_config(sorted_configs[2], 1, "MCI")
    mci2 = clean_and_rename_config(sorted_configs[3], 2, "MCI")

    # انتخاب کانفیگ‌های بعدی برای ایرانسل
    mtn1 = clean_and_rename_config(sorted_configs[4], 1, "Irancell")
    mtn2 = clean_and_rename_config(sorted_configs[5], 2, "Irancell")

    # چینش متن نهایی کانال VIP
    caption = (
        "👑 <b>کانفیگ اختصاصی اعضای VIP کاسپین</b> 👑\n\n"
        "♨️ <b>کانفیگ‌های پرسرعت و تست‌شده اختصاصی:</b>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص همراه اول:</b></a>\n'
        f"1️⃣ <code>{html.escape(mci1)}</code>\n\n"
        f"2️⃣ <code>{html.escape(mci2)}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص ایرانسل:</b></a>\n'
        f"1️⃣ <code>{html.escape(mtn1)}</code>\n\n"
        f"2️⃣ <code>{html.escape(mtn2)}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های دوکاره توربو (فوق‌سریع):</b></a>\n'
        f"1️⃣ <code>{html.escape(turbo1)}</code>\n\n"
        f"2️⃣ <code>{html.escape(turbo2)}</code>\n\n"
        "📶 <b>مناسب برای:</b> همراه اول، ایرانسل، رایتل و مخابرات 📊\n"
        "💡 <b>راهنما:</b> فقط کافیه روی هر کانفیگ یکبار ضربه بزنید تا خودکار کپی شود."
    )

    send_telegram_vip_message(caption)

    # آپدیت فایل ساب‌اسکریپشن
    sub_lines = [clean_and_rename_config(c, i, "VIP") for i, c in enumerate(sorted_configs, 1)]
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sub_lines))

    print(f"[✓] فایل sub.txt با {len(sub_lines)} کانفیگ بروزرسانی شد.")


if __name__ == "__main__":
    main()
