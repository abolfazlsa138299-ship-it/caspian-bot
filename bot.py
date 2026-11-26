import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@proxy_caspian")

def get_proxies_from_telmtproto():
    # اتصال مستقیم به کانال منبع مورد نظر شما
    url = "https://t.me/s/TelMTProto"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    collected = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r'href="(https://t\.me/proxy\?[^"]+)"', html)
            
            # استخراج از جدیدترین پیام‌ها (ته صفحه) به سمت بالا
            for m in reversed(matches):
                clean = m.replace("&amp;", "&")
                if clean not in collected:
                    collected.append(clean)
                if len(collected) == 4:
                    break
    except Exception as e:
        print(f"Error fetching from {url}: {e}")
        
    return collected

def send_to_channel(proxy_list):
    if not proxy_list:
        print("No proxies found to send.")
        return

    # دریافت سرور و پورت واقعی اولین پروکسی
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

    # چیدمان ۲ در ۲ دکمه‌ها بدون موشک
    p1 = proxy_list[0]
    p2 = proxy_list[1] if len(proxy_list) > 1 else p1
    p3 = proxy_list[2] if len(proxy_list) > 2 else p1
    p4 = proxy_list[3] if len(proxy_list) > 3 else p2

    keyboard_layout = [
        [
            {"text": "⚡️ Connect 1 ⚡️", "url": p1},
            {"text": "⚡️ Connect 2 ⚡️", "url": p2}
        ],
        [
            {"text": "⚡️ Connect 3 ⚡️", "url": p3},
            {"text": "⚡️ Connect 4 ⚡️", "url": p4}
        ],
        [
            {"text": "⚡️ عضویت در کانال کاسپین ⚡️", "url": "https://t.me/proxy_caspian"}
        ]
    ]

    payload = {
        "chat_id": CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": keyboard_layout},
        "disable_web_page_preview": True
    }

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            print("Successfully sent 4 TelMTProto proxies to Caspian channel!")
    except urllib.error.HTTPError as e:
        print(f"Failed to send: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("BOT_TOKEN is empty!")
        exit(1)
    
    proxies = get_proxies_from_telmtproto()
    if proxies:
        send_to_channel(proxies)
    else:
        print("No proxies retrieved from TelMTProto.")
