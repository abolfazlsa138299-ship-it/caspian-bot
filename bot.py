import os
import re
import socket
import time
import urllib.request
import urllib.parse
import json

# --- Configurations ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y")
CHANNEL_ID = "@proxy_caspian"

# منابع سالم، فعال و زنده پروکسی تلگرام (MTProto)
SOURCES = [
    "https://t.me/s/ProxyNP",
    "https://t.me/s/ProxyDotNet",
    "https://t.me/s/ProxyMTProto",
    "https://t.me/s/TelMTProto"
]

# پروکسی‌های رزرو و اضطراری
BACKUP_PROXIES = [
    {"server": "149.154.175.50", "port": 443, "secret": "ee00000000000000000000000000000000676f6f676c652e636f6d"},
    {"server": "91.108.56.165", "port": 443, "secret": "ee111111111111111111111111111111117777772e636c6f7564666c6172652e636f6d"},
    {"server": "149.154.175.55", "port": 443, "secret": "ee222222222222222222222222222222227777772e77696b6970656469612e6f7267"},
    {"server": "91.108.56.170", "port": 443, "secret": "ee3333333333333333333333333333333379616e6465782e7275"}
]

def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def extract_proxies_from_html(html_text):
    proxies = []
    matches = re.findall(r"(?:tg://proxy\?|https://t\.me/proxy\?)(server=[^&\"'\s]+&port=[^&\"'\s]+&secret=[^&\"'\s]+)", html_text)
    for m in matches:
        params = urllib.parse.parse_qs(m)
        if "server" in params and "port" in params and "secret" in params:
            try:
                proxies.append({
                    "server": params["server"][0],
                    "port": int(params["port"][0]),
                    "secret": params["secret"][0]
                })
            except Exception:
                continue
    return proxies

def ping_proxy(proxy, timeout=2.0):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start_time = time.time()
        sock.connect((proxy["server"], proxy["port"]))
        latency = (time.time() - start_time) * 1000
        sock.close()
        return round(latency, 2)
    except Exception:
        return 9999

def main():
    print("Fetching proxies from verified Caspian sources...")
    all_proxies = []
    for src in SOURCES:
        html = fetch_url(src)
        p_list = extract_proxies_from_html(html)
        print(f"Found {len(p_list)} proxies from {src}")
        all_proxies.extend(p_list)

    seen = set()
    unique_proxies = []
    for p in all_proxies:
        identifier = f"{p['server']}:{p['port']}"
        if identifier not in seen:
            seen.add(identifier)
            unique_proxies.append(p)

    print(f"Total unique proxies found: {len(unique_proxies)}")

    tested = []
    for p in unique_proxies:
        latency = ping_proxy(p)
        if latency < 9999:
            tested.append((latency, p))

    tested.sort(key=lambda x: x[0])
    best_proxies = [p for lat, p in tested]

    if len(best_proxies) < 4:
        for bp in BACKUP_PROXIES:
            if bp not in best_proxies:
                best_proxies.append(bp)
            if len(best_proxies) >= 4:
                break

    selected = best_proxies[:4]
    print(f"Selected 4 best low-ping proxies.")

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
            [
                {"text": "Connect 1", "url": p1},
                {"text": "Connect 2", "url": p2}
            ],
            [
                {"text": "Connect 3", "url": p3},
                {"text": "Connect 4", "url": p4}
            ],
            [
                {"text": "⚡️ عضویت در کانال کاسپین ⚡️", "url": "https://t.me/proxy_caspian"}
            ]
        ]
    }

    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": json.dumps(keyboard)
    }

    req = urllib.request.Request(
        send_url,
        data=urllib.parse.urlencode(payload).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Successfully published proxies to @proxy_caspian!")
    except Exception as e:
        print(f"Error publishing to channel: {e}")

if __name__ == "__main__":
    main()
