import os
import re
import json
import random
import urllib.request
import urllib.parse

# دریافت اطلاعات از متغیرهای امن
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@proxy_caspian")

def get_latest_proxies():
    sources = ["https://t.me/s/TelMTProto", "https://t.me/s/ProxyMTProto"]
    proxies = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for url in sources:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                matches = re.findall(r'href="(https://t\.me/proxy\?[^"]+)"', html)
                for m in matches:
                    clean_url = m.replace("&amp;", "&")
                    if clean_url not in proxies:
                        proxies.append(clean_url)
        except Exception as e:
            print(f"Error fetching: {e}")
    return proxies

def send_to_channel(proxy_url):
    parsed = urllib.parse.urlparse(proxy_url)
    params = urllib.parse.parse_qs(parsed.query)
    server = params.get("server", ["Unknown"])[0]
    port = params.get("port", ["Unknown"])[0]

    emojis = ["⚡️", "🚀", "🌊", "🔥"]
    emoji = random.choice(emojis)

    caption = (
        f"🌊 **پروکسی کاسپین | Caspian Proxy**\n\n"
        f"{emoji} **پروکسی پرسرعت و ضدفیلتر MTProto**\n"
        f"📡 سرور: `{server}`\n"
        f"🔌 پورت: `{port}`\n"
        f"📶 مخصوص: همراه اول، ایرانسل و رایتل ⚡️\n\n"
        f"🤍 با فوروارد کردن از ما حمایت کنید\n"
        f"🆔 @proxy_caspian"
    )

    keyboard = {
        "inline_keyboard": [
            [{"text": "⚡️ اتصال به پروکسی (Connect) ⚡️", "url": proxy_url}],
            [{"text": "🌊 عضویت در کانال کاسپین 🌊", "url": "https://t.me/proxy_caspian"}]
        ]
    }

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": caption,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard),
        "disable_web_page_preview": True
    }

    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            print("Successfully sent to channel!")
    except Exception as e:
        print("Failed to send:", e)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is empty!")
        exit(1)
    proxies = get_latest_proxies()
    if proxies:
        selected = proxies[-1]
        send_to_channel(selected)
    else:
        print("No proxies found.")
