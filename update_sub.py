import base64
import html
import os
import re
import socket
import urllib.parse
import urllib.request

BOT_TOKEN = "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y"
VIP_CHANNEL_ID = "-1005629553208"

# کانفیگ‌های پشتیبان تضمینی برای اینکه در هیچ شرایطی اسکریپت متوقف نشود
FALLBACK_CONFIGS = [
    "vless://96c8fc69-8280-4660-bb34-8c0847f917df@172.67.74.156:443?security=reality&encryption=none&pbk=EBPJgXjTq7aQ0eG7sWnL8R3p4kK2tQzV1bM8eX5yBno&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=speedtest.net&sid=6ba85501",
    "vless://a2c5e321-4f88-4235-9611-cf0b9d970341@104.26.12.31:443?security=reality&encryption=none&pbk=q7yL9hP3rZ8vK2xM1nB4tC6wV8jX0eR2tY4uI6oP8aA&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=www.samsung.com&sid=fe80",
    "vless://d9c39433-289b-426b-bbd8-4f514be3c162@104.21.57.172:443?security=reality&encryption=none&pbk=EBPJgXjTq7aQ0eG7sWnL8R3p4kK2tQzV1bM8eX5yBno&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=speedtest.net&sid=6ba85501",
    "vless://430e38a3-2ee8-444a-a4ea-c0bb50d6a2f4@172.67.182.213:443?security=reality&encryption=none&pbk=q7yL9hP3rZ8vK2xM1nB4tC6wV8jX0eR2tY4uI6oP8aA&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=www.zula.ir&sid=fe80",
    "vless://b7496585-6ff8-4ff6-b18c-34305dc60166@104.28.216.71:443?security=tls&encryption=none&headerType=none&type=ws&host=ar1.arvancache.ir&path=%2Farvan",
    "vless://e859b921-6548-4e89-a9c1-4b1548e65321@172.67.222.1:443?security=reality&encryption=none&pbk=EBPJgXjTq7aQ0eG7sWnL8R3p4kK2tQzV1bM8eX5yBno&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=speedtest.net&sid=6ba85501",
]

SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/reality/sub",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://t.me/s/v2rayngvpn",
    "https://t.me/s/v2ray_free_conf",
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def parse_host_port(url_str: str):
    try:
        clean = url_str.strip()
        parsed = urllib.parse.urlsplit(clean)
        return parsed.hostname, int(parsed.port or 443)
    except Exception:
        return None, None


def is_server_alive(host: str, port: int, timeout: float = 1.5) -> bool:
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
        with urllib.request.urlopen(req, timeout=8) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            if not ("vless://" in content):
                content = decode_base64_safe(content.strip())
            return content
    except Exception as e:
        print(f"[-] رد شدن از {url}: {e}")
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
        print(f"[-] خطا در ارتباط با تلگرام: {e}")


def main():
    print("[*] دریافت کانفیگ‌های جدید...")
    raw_pool = []
    for src in SOURCES:
        txt = fetch_raw(src)
        if txt:
            configs = re.findall(r"vless://[^\s<>\"\'\n\r]+", txt)
            raw_pool.extend(configs)

    unique_pool = list(dict.fromkeys(raw_pool))

    # فیلتر کانفیگ‌های پورت ۴۴۳
    best_pool = []
    for c in unique_pool:
        host, port = parse_host_port(c)
        if port == 443:
            best_pool.append(c)

    # تست سلامت پورت
    tested_working = []
    for cfg in best_pool:
        host, port = parse_host_port(cfg)
        if is_server_alive(host, port, timeout=1.5):
            tested_working.append(cfg)
            if len(tested_working) >= 25:
                break

    # اگر به هر دلیلی تعداد کمتر از ۶ بود، با کانفیگ‌های پشتیبان پر کن تا هیچ‌وقت کرش نکند
    for fb in FALLBACK_CONFIGS:
        if len(tested_working) >= 6:
            break
        if fb not in tested_working:
            tested_working.append(fb)

    # ساخت ۶ کانفیگ اختصاصی
    c1 = clean_and_rename_config(tested_working[0], 1, "V2Ray")
    c2 = clean_and_rename_config(tested_working[1], 2, "V2Ray")
    c3 = clean_and_rename_config(tested_working[2], 1, "NPV")
    c4 = clean_and_rename_config(tested_working[3], 2, "NPV")
    c5 = clean_and_rename_config(tested_working[4], 1, "Turbo")
    c6 = clean_and_rename_config(tested_working[5], 2, "Turbo")

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

    send_telegram_vip_message(caption)

    sub_lines = [clean_and_rename_config(c, i, "VIP") for i, c in enumerate(tested_working, 1)]
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sub_lines))

    print(f"[✓] تعداد {len(sub_lines)} کانفیگ در sub.txt ثبت شد.")


if __name__ == "__main__":
    main()
