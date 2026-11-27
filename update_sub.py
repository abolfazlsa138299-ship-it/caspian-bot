import base64
import html
import os
import re
import socket
import time
import urllib.parse
import urllib.request

BOT_TOKEN = "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y"
VIP_CHANNEL_ID = "-1005629553208"

# ۶ کانال اصلی و مرجع تلگرام برای استخراج لحظه‌ای
TARGET_CHANNELS = [
    "https://t.me/s/Hope_Net",
    "https://t.me/s/v2rayngvpn",
    "https://t.me/s/v2ray_free_conf",
    "https://t.me/s/customv2ray",
    "https://t.me/s/Freetech2024",
    "https://t.me/s/PrivateVPNs",
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def parse_host_port(url_str: str):
    """استخراج هاست و پورت کانفیگ برای تست پینگ"""
    try:
        clean = url_str.strip()
        parsed = urllib.parse.urlsplit(clean)
        host = parsed.hostname
        port = parsed.port or 443
        return host, int(port)
    except Exception:
        return None, None


def test_latency(host: str, port: int, timeout: float = 1.5) -> float:
    """تست زنده بودن و محاسبه پینگ (تاخیر زمانی) دقیقاً مثل پروکسی‌بات"""
    if not host or not port:
        return 9999.0
    try:
        start = time.time()
        with socket.create_connection((host, port), timeout=timeout):
            latency = (time.time() - start) * 1000
            return round(latency, 1)
    except Exception:
        return 9999.0


def fetch_channel_configs(channel_url: str) -> list:
    """اسکرپ زنده آخرین پست‌های کانال تلگرامی"""
    try:
        req = urllib.request.Request(channel_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            # استخراج کانفیگ‌های موجود در پست‌ها
            found = re.findall(r"(?:vless|vmess|trojan)://[^\s<>\"\'\n\r]+", content)
            # برداشتن جدیدترین پست‌ها (آخرین کانفیگ‌های هر کانال)
            latest = found[-15:] if len(found) > 15 else found
            return latest
    except Exception as e:
        print(f"[-] خطا در دریافت از {channel_url}: {e}")
        return []


def clean_and_rename_config(config_str: str, index: int, label: str) -> str:
    """تغییر نام کانفیگ به برند شکیل کاسپین"""
    raw_config = config_str.split("#")[0].strip()
    tag = urllib.parse.quote(f"Caspian-{label}-{index} ⚡ @proxy_caspian")
    return f"{raw_config}#{tag}"


def send_telegram_vip_message(caption: str):
    """ارسال پست به کانال VIP"""
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
            print("[+] پست کانال VIP با موفقیت منتشر شد.")
    except Exception as e:
        print(f"[-] خطا در ارسال پیام به کانال VIP: {e}")


def main():
    print("[*] در حال اسکن ۶ کانال منتخب تلگرام...")
    all_extracted = []

    for chan in TARGET_CHANNELS:
        cfgs = fetch_channel_configs(chan)
        print(f"[+] از {chan} تعداد {len(cfgs)} کانفیگ جدید استخراج شد.")
        all_extracted.extend(cfgs)

    # حذف تکراری‌ها و معکوس کردن برای اولویت دادن به تازه‌ترین‌ها
    unique_pool = list(dict.fromkeys(reversed(all_extracted)))
    print(f"[*] کل کانفیگ‌های یکتا: {len(unique_pool)}")

    print("[*] در حال تحلیل، تست اتصال و مرتب‌سازی بر اساس کمترین پینگ...")
    working_pool = []

    for cfg in unique_pool:
        host, port = parse_host_port(cfg)
        if host and port:
            ping = test_latency(host, port, timeout=1.5)
            if ping < 9999.0:
                working_pool.append((ping, cfg))
                print(f"  [✓ سالم] {host}:{port} - پینگ: {ping}ms")
                if len(working_pool) >= 40:
                    break

    # مرتب‌سازی بر اساس کمترین پینگ (سریع‌ترین‌ها در اولویت)
    working_pool.sort(key=lambda x: x[0])
    best_configs = [item[1] for item in working_pool]

    # اگر به هر دلیلی تعداد کمتر از ۶ بود، از کانفیگ‌های اولیه پر کن
    if len(best_configs) < 6:
        for c in unique_pool:
            if c not in best_configs:
                best_configs.append(c)
            if len(best_configs) >= 6:
                break

    # آماده‌سازی ۶ کانفیگ گلچین با نام‌گذاری کاسپین
    c1 = clean_and_rename_config(best_configs[0], 1, "V2Ray")
    c2 = clean_and_rename_config(best_configs[1], 2, "V2Ray")
    c3 = clean_and_rename_config(best_configs[2], 1, "NPV")
    c4 = clean_and_rename_config(best_configs[3], 2, "NPV")
    c5 = clean_and_rename_config(best_configs[4], 1, "Turbo")
    c6 = clean_and_rename_config(best_configs[5], 2, "Turbo")

    # فرمت نهایی و شکیل پیام VIP با تیتری که مشخص کردی
    caption = (
        "👑 <b>کانفیگ اختصاصی اعضای VIP کاسپین</b> 👑\n\n"
        "♨️ <b>کانفیگ‌های پرسرعت و تست‌شده اختصاصی:</b>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص V2Ray:</b></a>\n'
        f"1️⃣ <code>{html.escape(c1)}</code>\n\n"
        f"2️⃣ <code>{html.escape(c2)}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص NPV Tunnel:</b></a>\n'
        f"1️⃣ <code>{html.escape(c3)}</code>\n\n"
        f"2️⃣ <code>{html.escape(c4)}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های دوکاره (توربو):</b></a>\n'
        f"1️⃣ <code>{html.escape(c5)}</code>\n\n"
        f"2️⃣ <code>{html.escape(c6)}</code>\n\n"
        "📶 <b>مناسب برای:</b> همراه اول، ایرانسل، رایتل و مخابرات 📊\n"
        "💡 <b>راهنما:</b> فقط کافیه روی هر کانفیگ یکبار ضربه بزنید تا خودکار کپی شود."
    )

    # ۱. ارسال پست به کانال VIP
    send_telegram_vip_message(caption)

    # ۲. ذخیره تمام کانفیگ‌های تست شده سالم داخل فایل ساب‌اسکریپشن
    sub_lines = [clean_and_rename_config(c, i, "VIP") for i, c in enumerate(best_configs, 1)]
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sub_lines))

    print(f"[✓] فایل sub.txt با موفقیت آپدیت شد.")


if __name__ == "__main__":
    main()
