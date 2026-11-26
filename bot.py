import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@proxy_caspian")

def fetch_fresh_proxy_from_channel(channel_url):
    """برداشتن جدیدترین و داغ‌ترین پروکسی از کانال معتبر"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        req = urllib.request.Request(channel_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # پیدا کردن تمام پروکسی‌های معتبر
            matches = re.findall(r'href="(https://t\.me/proxy\?[^"]+)"', html)
            
            # جستجو از جدیدترین پیام‌ها به عقب برای پروکسی Fake TLS
            for m in reversed(matches):
                clean_url = m.replace("&amp;", "&")
                if "secret=ee" in clean_url or "secret=7" in clean_url:
                    return clean_url
            # اگر با سکرت ee پیدا نشد آخرین پروکسی منتشر شده را بدهد
            if matches:
                return matches[-1].replace("&amp;", "&")
    except Exception as e:
        print(f"Error fetching from {channel_url}: {e}")
    return None

def get_top_proxies():
    # فعال‌ترین کانال‌های پروکسی زنده و پرسرعت برای ایران
    sources = [
        "https://t.me/s/FalconProxy",
        "https://t.me/s/ProxyMTProto_Tel",
        "https://t.me/s/ProxyDaemi"
    ]
    
    selected_proxies = []
    for src in sources:
        p = fetch_fresh_proxy_from_channel(src)
        if p and p not in selected_proxies:
            selected_proxies.append(p)
            
    return selected_proxies

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
            print("Successfully sent 3 fresh proxies!")
    except urllib.error.HTTPError as e:
        print(f"Failed to send: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is empty!")
        exit(1)
    
    fresh_proxies = get_top_proxies()
    if fresh_proxies:
        send_to_channel(fresh_proxies)
    else:
        print("No fresh proxies found.")
