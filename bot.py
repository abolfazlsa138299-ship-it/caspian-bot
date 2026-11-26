import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@proxy_caspian")

def get_live_working_proxies():
    # مخازن زنده و مستقیم پروکسی‌های فعال نت ایران (آپدیت لحظه‌ای)
    api_endpoints = [
        "https://raw.githubusercontent.com/yebekhe/Telegram-Proxy/master/mtproto.json",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.json",
        "https://raw.githubusercontent.com/Surfboardv2ray/TG-Proxy/main/mtproto.json"
    ]
    
    found_proxies = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for endpoint in api_endpoints:
        try:
            req = urllib.request.Request(endpoint, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read().decode("utf-8")
                # بررسی داده‌های JSON یا متنی
                try:
                    json_data = json.loads(data)
                    for item in json_data:
                        # استخراج مشخصات پروکسی
                        server = item.get("server") or item.get("host")
                        port = item.get("port")
                        secret = item.get("secret")
                        if server and port and secret:
                            proxy_link = f"https://t.me/proxy?server={server}&port={port}&secret={secret}"
                            if proxy_link not in found_proxies:
                                found_proxies.append(proxy_link)
                except:
                    matches = re.findall(r'https://t\.me/proxy\?[^\s"\'<>]+', data)
                    for m in matches:
                        clean_m = m.replace("&amp;", "&")
                        if clean_m not in found_proxies:
                            found_proxies.append(clean_m)
        except Exception as e:
            print(f"Error fetching from {endpoint}: {e}")

    # تفکیک پروکسی‌های Fake TLS (سکرت با ee شروع می‌شود - مخصوص دانلود پرسرعت)
    ee_proxies = [p for p in found_proxies if "secret=ee" in p]
    if len(ee_proxies) >= 4:
        return ee_proxies[:4]
    
    return found_proxies[:4]

def send_to_channel(proxy_list):
    parsed = urllib.parse.urlparse(proxy_list[0])
    params = urllib.parse.parse_qs(parsed.query)
    server = params.get("server", ["Caspian-Node"])[0]
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

    # چیدمان دقیق ۲ در ۲ و دکمه عضویت زیر آنها
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
            print("Successfully sent 4 live API proxies!")
    except urllib.error.HTTPError as e:
        print(f"Failed to send: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("BOT_TOKEN is empty!")
        exit(1)
    
    proxies = get_live_working_proxies()
    if proxies:
        send_to_channel(proxies)
    else:
        print("No live proxies found.")
