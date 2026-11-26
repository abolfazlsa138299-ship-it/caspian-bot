import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@proxy_caspian")

def fetch_proxies_from_source(url):
    proxies = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r'href="(https://t\.me/proxy\?[^"]+)"', html)
            for m in reversed(matches):
                clean_url = m.replace("&amp;", "&")
                # فیلتر پروکسی‌های ضدفیلتر و Fake TLS واقعی
                if "secret=ee" in clean_url or "secret=7" in clean_url:
                    proxies.append(clean_url)
    except Exception as e:
        print(f"Error fetching from {url}: {e}")
    return proxies

def get_4_top_proxies():
    # ۶ منبع قدرتمند و فعال برای نت ایران
    sources = [
        "https://t.me/s/FalconProxy",
        "https://t.me/s/ProxyMTProto_Tel",
        "https://t.me/s/TelMTProto",
        "https://t.me/s/ProxyDaemi",
        "https://t.me/s/iMTProto",
        "https://t.me/s/MTP_roxy"
    ]
    
    collected_proxies = []
    for src in sources:
        proxies = fetch_proxies_from_source(src)
        if proxies:
            latest = proxies[0]
            if latest not in collected_proxies:
                collected_proxies.append(latest)
        if len(collected_proxies) == 4:
            break
            
    return collected_proxies

def send_to_channel(proxy_list):
    parsed = urllib.parse.urlparse(proxy_list[0])
    params = urllib.parse.parse_qs(parsed.query)
    server = params.get("server", ["Caspian-Core"])[0]
    port = params.get("port", ["443"])[0]

    caption = (
        "⚡️ <b>پروکسی کاسپین | PROXY</b>\n\n"
        "⚡️ <b>پروکسی پرسرعت و ضدفیلتر Caspian</b>\n"
        f"📡 سرور: <code>{server}</code>\n"
        f"🔌 پورت: <code>{port}</code>\n"
        "📶 مخصوص: همراه اول، ایرانسل و رایتل ⚡️\n\n"
        "🤍 با فوروارد کردن از ما حمایت کنید\n"
        "🆔 @proxy_caspian"
    )

    # چیدمان دکمه‌ها به صورت ۲ در ۲ (دوتایی کنار هم)
    keyboard_layout = [
        [
            {"text": "⚡️ Connect 1 ⚡️", "url": proxy_list[0]},
            {"text": "⚡️ Connect 2 ⚡️", "url": proxy_list[1] if len(proxy_list) > 1 else proxy_list[0]}
        ],
        [
            {"text": "⚡️ Connect 3 ⚡️", "url": proxy_list[2] if len(proxy_list) > 2 else proxy_list[0]},
            {"text": "⚡️ Connect 4 ⚡️", "url": proxy_list[3] if len(proxy_list) > 3 else proxy_list[0]}
        ],
        [
            {"text": "⚡️ عضویت در کانال کاسپین ⚡️", "url": "https://t.me/proxy_caspian"}
        ]
    ]

    keyboard = {"inline_keyboard": keyboard_layout}

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
            print("Successfully sent 4 proxies in 2x2 layout!")
    except urllib.error.HTTPError as e:
        print(f"Failed to send: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is empty!")
        exit(1)
    
    top_proxies = get_4_top_proxies()
    if top_proxies:
        send_to_channel(top_proxies)
    else:
        print("No proxies found.")
