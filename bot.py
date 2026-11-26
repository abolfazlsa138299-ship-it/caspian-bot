
import os
import re
import json
import socket
import urllib.request
import urllib.parse
import urllib.error

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@proxy_caspian")

def check_proxy_alive(server, port, timeout=1.8):
    """تست واقعی اتصال و پینگ سرور در کسری از ثانیه"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((server, int(port)))
        sock.close()
        return result == 0  # 0 یعنی سرور فعال و پینگ عالی است
    except:
        return False

def get_live_highspeed_proxies():
    sources = [
        "https://t.me/s/FalconProxy",
        "https://t.me/s/ProxyMTProto_Tel",
        "https://t.me/s/ProxyDaemi",
        "https://t.me/s/iMTProto",
        "https://t.me/s/IRN_VPN"
    ]
    raw_proxies = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for url in sources:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                matches = re.findall(r'href="(https://t\.me/proxy\?[^"]+)"', html)
                for m in matches:
                    clean_url = m.replace("&amp;", "&")
                    # حتما فیک‌تی‌ال‌اس باشد
                    if "secret=ee" in clean_url and clean_url not in raw_proxies:
                        raw_proxies.append(clean_url)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # برعکس کردن لیست برای تست از جدیدترین به قدیمی‌ترین
    raw_proxies.reverse()

    verified_proxies = []
    print("Testing proxies latency and availability...")

    for p in raw_proxies:
        parsed = urllib.parse.urlparse(p)
        params = urllib.parse.parse_qs(parsed.query)
        server = params.get("server", [None])[0]
        port = params.get("port", [None])[0]

        if server and port:
            # ربات خودش پورت و سرور را تست پینگ می‌کند
            if check_proxy_alive(server, port):
                print(f"✅ Verified Alive: {server}:{port}")
                verified_proxies.append(p)
                if len(verified_proxies) == 3:
                    break
            else:
                print(f"❌ Dead/Slow Proxy skipped: {server}:{port}")

    return verified_proxies

def send_to_channel(proxy_list):
    parsed = urllib.parse.urlparse(proxy_list[0])
    params = urllib.parse.parse_qs(parsed.query)
    server = params.get("server", ["Caspian-Core"])[0]
    port = params.get("port", ["443"])[0]

    caption = (
        "⚡️ <b>پروکسی کاسپین | PROXY</b>\n\n"
        "🚀 <b>پروکسی پرسرعت و ضدفیلتر Caspian</b>\n"
        f"📡 سرور: <code>{server}</code>\n"
        f"🔌 پورت: <code>{port}</code>\n"
        "📶 مخصوص: همراه اول، ایرانسل و رایتل ⚡️\n\n"
        "🤍 با فوروارد کردن از ما حمایت کنید\n"
        "🆔 @proxy_caspian"
    )

    buttons = []
    numbers = ["۱", "۲", "۳"]
    for i, p_url in enumerate(proxy_list):
        num = numbers[i] if i < len(numbers) else str(i+1)
        buttons.append([{"text": f"⚡️ اتصال به پروکسی {num} (Connect {i+1}) ⚡️", "url": p_url}])

    buttons.append([{"text": "🚀 عضویت در کانال کاسپین 🚀", "url": "https://t.me/proxy_caspian"}])

    keyboard = {"inline_keyboard": buttons}

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "reply_markup": keyboard,
        "disable_web_page_preview": True
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            print("Successfully sent 3 tested live proxies!")
    except urllib.error.HTTPError as e:
        print(f"Failed to send: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is empty!")
        exit(1)
    
    live_proxies = get_live_highspeed_proxies()
    if live_proxies:
        send_to_channel(live_proxies)
    else:
        print("No alive fast proxies found in this cycle.")
