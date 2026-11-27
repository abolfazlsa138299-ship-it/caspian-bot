import base64
import html
import os
import re
import socket
import urllib.parse
import urllib.request

# تنظیمات اصلی
BOT_TOKEN = "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y"
VIP_CHANNEL_ID = "-1005629553208"

# کانال‌ها و سورس‌های داغ و لحظه‌ای تلگرام که کانفیگ‌های فعال ایران می‌گذارند
SOURCES = [
    "https://t.me/s/v2rayngvpn",
    "https://t.me/s/customv2ray",
    "https://t.me/s/v2ray_free_conf",
    "https://t.me/s/Hope_Net",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/normal/vless",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


def parse_host_port(url_str: str):
    try:
        clean = url_str.strip()
        parsed = urllib.parse.urlsplit(clean)
        return parsed.hostname, int(parsed.port or 443)
    except Exception:
        return None, None


def is_server_alive(host: str, port: int, timeout: float = 2.0) -> bool:
    if not host or not port:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def decode_base64_safe(data_str: str) -> str:
    try:
        padding = 4 - (len(data_str) % 4)
        if padding != 4:
            data_str += "=" * padding
        return base64.b64decode(data_str).decode("utf-8", errors="ignore")
    except Exception:
        return data_str


def fetch_raw(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            if not ("vless://" in content or "vmess://" in content):
                content = decode_base64_safe(content.strip())
            return content
    except Exception as e:
        print(f"[-] خطا در دریافت از {url}: {e}")
        return ""


def clean_and_rename_config(config_str: str, index: int, label: str) -> str:
    raw_config = config_str.split("#")[0].strip()
    tag = urllib.parse.quote(f"Caspian-{label}-{index} ⚡ @proxy_caspian")
    return f"{raw_config}#{tag}"


def send_telegram_vip_message(caption: str):
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
    except urllib.error.HTTPError as e:
        print(f"[-] خطای تلگرام ({e.code}): {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[-] خطای اتصال به تلگرام: {e}")


def main():
    print("[*] دریافت کانفیگ‌های تازه از کانال‌های تلگرامی...")
    raw_pool = []
    for src in SOURCES:
        txt = fetch_raw(src)
        if txt:
            # استخراج کانفیگ‌های vless و trojan
            configs = re.findall(r"(?:vless|trojan)://[^\s<>\"\'\n\r]+", txt)
            raw_pool.extend(configs)

    unique_pool = list(dict.fromkeys(raw_pool))
    print(f"[*] کل کانفیگ‌های یکتا: {len(unique_pool)}")

    # اولویت با کانفیگ‌های پورت ۴۴۳ و ریالیتی
    best_configs = []
    for c in unique_pool:
        host, port = parse_host_port(c)
        if port == 443:
            best_configs.append(c)

    if len(best_configs) < 20:
        best_configs = unique_pool

    # تست زنده بودن اتصال سرورها
    tested_working = []
    for cfg in best_configs:
        host, port = parse_host_port(cfg)
        if is_server_alive(host, port, timeout=1.8):
            tested_working.append(cfg)
            if len(tested_working) >= 30:
                break

    if len(tested_working) < 6:
        tested_working = best_configs[:6]

    # ساخت ۶ کانفیگ اختصاصی با نام کاسپین
    c1 = clean_and_rename_config(tested_working[0], 1, "V2Ray")
    c2 = clean_and_rename_config(tested_working[1], 2, "V2Ray")
    c3 = clean_and_rename_config(tested_working[2], 1, "NPV")
    c4 = clean_and_rename_config(tested_working[3], 2, "NPV")
    c5 = clean_and_rename_config(tested_working[4], 1, "Turbo")
    c6 = clean_and_rename_config(tested_working[5], 2, "Turbo")

    # مهم: انکود کردن کاراکترهای & با html.escape تا تلگرام ارور ندهد
    caption = (
        "👑 <b>کانفیگ اختصاصی اعضای VIP کاسپین</b> 👑\n\n"
        "♨️ <b>کانفیگ‌های تازه‌نفس و ضد فیلتر کاسپین:</b>\n\n"
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

    # ارسال به کانال VIP
    send_telegram_vip_message(caption)

    # ذخیره در فایل ساب‌اسکریپشن
    sub_lines = [clean_and_rename_config(c, i, "VIP") for i, c in enumerate(tested_working, 1)]
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sub_lines))

    print(f"[✓] فایل sub.txt با {len(sub_lines)} کانفیگ بروزرسانی شد.")


if __name__ == "__main__":
    main()
