import os
import re
import socket
import time
import html
import urllib.request
import urllib.parse
import json

BOT_TOKEN = os.environ.get("BOT_TOKEN", "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y")
CHANNEL_ID = "@proxy_caspian"

SOURCES = [
    "https://t.me/s/ProxyNP",
    "https://t.me/s/ProxyDotNet",
    "https://t.me/s/TelMTProto",
    "https://t.me/s/ProxyMTProto"
]

def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Fetch failed: {e}")
        return ""

def extract_proxies(raw_html):
    clean_html = html.unescape(raw_html)
    proxies = []
    pattern = r"(?:https://t\.me/proxy\?|tg://proxy\?)([^\s\"'<>]+)"
    matches = re.findall(pattern, clean_html)
    
    for qs in matches:
        try:
            parsed = urllib.parse.parse_qs(qs)
            server = parsed.get("server", [None])[0]
            port = parsed.get("port", [None])[0]
            secret = parsed.get("secret", [None])[0]
            if server and port and secret:
                proxies.append({
                    "server": server.strip(),
                    "port": int(port.strip()),
                    "secret": secret.strip()
                })
        except Exception:
            continue
    return proxies

def ping_proxy(proxy):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.5)
        start = time.time()
        sock.connect((proxy["server"], proxy["port"]))
        lat = (time.time() - start) * 1000
        sock.close()
        return round(lat, 2)
    except Exception:
        return 9999

def main():
    print("Scraping live proxies for @proxy_caspian...")
    all_proxies = []
    for src in SOURCES:
        content = fetch_url(src)
        p_list = extract_proxies(content)
        all_proxies.extend(p_list)

    seen = set()
    unique = []
    for p in all_proxies:
        key = f"{p['server']}:{p['port']}"
        if key not in seen:
            seen.add(key)
            unique.append(p)

    if not unique:
        print("No proxies found from channels.")
        return

    tested = []
    for p in unique:
        lat = ping_proxy(p)
        if lat < 9999:
            tested.append((lat, p))

    tested.sort(key=lambda x: x[0])
    selected = [p for lat, p in tested][:4]

    if len(selected) < 4:
        selected = unique[:4]

    p1 = f"https://t.me/proxy?server={selected[0]['server']}&port={selected[0]['port']}&secret={selected[0]['secret']}"
    p2 = f"https://t.me/proxy?server={selected[1]['server']}&port={selected[1]['port']}&secret={selected[1]['secret']}"
    p3 = f"https://t.me/proxy?server={selected[2]['server']}&port={selected[2]['port']}&secret={selected[2]['secret']}"
    p4 = f"https://t.me/proxy?server={selected[3]['server']}&port={selected[3]['port']}&secret={selected[3]['secret']}"

    caption = (
        "⚡️ <b>پروکسی‌های پرسرعت و ضد فیلتر کاسپین</b>\n\n"
        "▫️ پینگ پایین و اتصال فوری\n"
        "▫️ مناسب همراه اول، ایرانسل، رایتل و مخابرات\n"
        "▫️ بدون افت سرعت در دانلود و تماشای ویدیو\n\n"
        "💡 <i>در صورت کندی یک سرور، به سرور بعدی متصل شوید.</i>\n\n"
        "🆔 @proxy_caspian"
    )

    keyboard = {
        "inline_keyboard": [
            [{"text": "Connect 1", "url": p1}, {"text": "Connect 2", "url": p2}],
            [{"text": "Connect 3", "url": p3}, {"text": "Connect 4", "url": p4}],
            [{"text": "⚡️ عضویت در کانال کاسپین ⚡️", "url": "https://t.me/proxy_caspian"}]
        ]
    }

    payload = {
        "chat_id": CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": json.dumps(keyboard)
    }

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=urllib.parse.urlencode(payload).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    urllib.request.urlopen(req, timeout=10)
    print("Proxies published successfully.")

if __name__ == "__main__":
    main()
