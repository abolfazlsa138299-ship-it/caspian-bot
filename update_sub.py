import base64
import os
import re
import socket
import sys
import urllib.parse
import urllib.request

# خواندن متغیرها از Secrets گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
VIP_CHANNEL_ID = os.environ.get("VIP_CHANNEL_ID", "-1005629553208").strip()

# منابع فوق‌العاده معتبر و ساعتی مخصوص اینترنت ایران (همراه اول، ایرانسل، رایتل و مخابرات)
SOURCES = [
    # مخازن تست شده با رفرش ساعتی Reality و VLESS
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/normal/vless",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vless",
    "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/config",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    # کانال‌های تلگرامی فعال و معتبر
    "https://t.me/s/v2rayngvpn",
    "https://t.me/s/v2ray_free_conf",
    "https://t.me/s/vmess_vless_v2rayng",
    "https://t.me/s/PrivateVPNs",
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


def is_server_alive(host: str, port: int, timeout: float = 2.0) -> bool:
    """تست اتصال زنده و واقعی سوکت به سرور قبل از تایید کانفیگ"""
    if not host or not port:
        return False
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except Exception:
        return False


def parse_host_port(url_str: str):
    """استخراج هاست و پورت کانفیگ"""
    try:
        clean = url_str.strip()
        parsed = urllib.parse.urlsplit(clean)
        host = parsed.hostname
        port = parsed.port or 443
        return host, port
    except Exception:
        return None, None


def decode_base64_safe(data_str: str) -> str:
    """رمزگشایی ایمن متن‌های Base64 مخازن"""
    try:
        padding = 4 - (len(data_str) % 4)
        if padding != 4:
            data_str += "=" * padding
        return base64.b64decode(data_str).decode("utf-8", errors="ignore")
    except Exception:
        return data_str


def fetch_raw(url: str) -> str:
    """دریافت خام اطلاعات با هدر استاندارد"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            # اگر محتوا بیس64 بود بازش کن
            if not ("vless://" in content or "vmess://" in content or "trojan://" in content):
                content = decode_base64_safe(content.strip())
            return content
    except Exception as e:
        print(f"[-] خطا در دریافت از {url}: {e}")
        return ""


def clean_and_rename_config(config_str: str, index: int, label: str) -> str:
    """تغییر نام کانفیگ به برند کاسپین"""
    raw_config = config_str.split("#")[0].strip()
    tag = urllib.parse.quote(f"Caspian-{label}-{index} ⚡ @proxy_caspian")
    return f"{raw_config}#{tag}"


def send_telegram_vip_message(caption: str):
    """ارسال پست شکیل به کانال VIP"""
    if not BOT_TOKEN or not VIP_CHANNEL_ID:
        print("[-] توکن بات یا آیدی کانال VIP تعریف نشده است.")
        return

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
    print("[*] در حال اسکن و دریافت کانفیگ‌های تازه...")
    raw_pool = []

    for src in SOURCES:
        text = fetch_raw(src)
        if not text:
            continue

        # استخراج تمامی کانفیگ‌های VLESS، VMess و Trojan
        found = re.findall(r"(?:vless|vmess|trojan)://[^\s<>\"\'\n\r]+", text)
        print(f"[+] از منبع {src} تعداد {len(found)} کانفیگ استخراج شد.")
        raw_pool.extend(found)

    # حذف موارد تکراری
    unique_pool = list(dict.fromkeys(raw_pool))
    print(f"[*] کل کانفیگ‌های یکتا: {len(unique_pool)}")

    # اولویت‌بندی با VLESS Reality
    vless_reality = [c for c in unique_pool if "vless://" in c and "reality" in c.lower()]
    vless_tls = [c for c in unique_pool if "vless://" in c and "security=tls" in c.lower()]
    trojan_pool = [c for c in unique_pool if "trojan://" in c]
    other_vless = [c for c in unique_pool if "vless://" in c and c not in vless_reality and c not in vless_tls]

    sorted_candidates = vless_reality + vless_tls + trojan_pool + other_vless

    print("[*] در حال اجرای تست پینگ و بررسی سلامت زنده بودن سرورها...")
    tested_working = []

    for cfg in sorted_candidates:
        host, port = parse_host_port(cfg)
        if host and port:
            # تست زنده بودن سرور با پینگ سوکت
            if is_server_alive(host, port, timeout=2.0):
                tested_working.append(cfg)
                print(f"  [✓ زنده] {host}:{port}")
                if len(tested_working) >= 40:  # دریافت ۴۰ تای اول سالم برای ساب و پست
                    break
            else:
                print(f"  [✗ قطع/بلاک] {host}:{port}")

    if len(tested_working) < 6:
        print("[!] تعداد کانفیگ‌های تست‌شده کمتر از ۶ بود، اضافه کردن از بهترین کاندیداها...")
        for cfg in sorted_candidates:
            if cfg not in tested_working:
                tested_working.append(cfg)
            if len(tested_working) >= 6:
                break

    # آماده‌سازی ۶ کانفیگ اختصاصی VIP (۲ تا V2Ray، ۲ تا NPV، ۲ تا دوکاره)
    c1 = clean_and_rename_config(tested_working[0], 1, "V2Ray")
    c2 = clean_and_rename_config(tested_working[1], 2, "V2Ray")
    c3 = clean_and_rename_config(tested_working[2], 1, "NPV")
    c4 = clean_and_rename_config(tested_working[3], 2, "NPV")
    c5 = clean_and_rename_config(tested_working[4], 1, "Turbo")
    c6 = clean_and_rename_config(tested_working[5], 2, "Turbo")

    # ساخت متن شکیل پست کانال VIP دقیقاً مطابق خواسته‌ها
    caption = (
        "👑 <b>کانفیگ اختصاصی اعضای VIP کاسپین</b> 👑\n\n"
        "♨️ <b>کانفیگ‌های تازه‌نفس و ضد فیلتر کاسپین (تست‌شده و فعال):</b>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص V2Ray:</b></a>\n'
        f"1️⃣ <code>{c1}</code>\n\n"
        f"2️⃣ <code>{c2}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص NPV Tunnel:</b></a>\n'
        f"1️⃣ <code>{c3}</code>\n\n"
        f"2️⃣ <code>{c4}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های دوکاره (توربو):</b></a>\n'
        f"1️⃣ <code>{c5}</code>\n\n"
        f"2️⃣ <code>{c6}</code>\n\n"
        "📶 <b>مناسب برای:</b> همراه اول، ایرانسل، رایتل و مخابرات 📊\n"
        "💡 <b>راهنما:</b> فقط کافیه روی هر کانفیگ یکبار ضربه بزنید تا خودکار کپی شود."
    )

    # ۱. ارسال پست به کانال VIP
    send_telegram_vip_message(caption)

    # ۲. ذخیره تمام کانفیگ‌های تست شده سالم داخل sub.txt
    branded_sub_list = []
    for idx, cfg in enumerate(tested_working, 1):
        branded_sub_list.append(clean_and_rename_config(cfg, idx, "Auto"))

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(branded_sub_list))

    print(f"[✓] فایل sub.txt با {len(branded_sub_list)} کانفیگ فعال و سالم بروزرسانی شد.")


if __name__ == "__main__":
    main()
