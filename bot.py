import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@proxy_caspian")

def get_high_speed_proxies():
    # منابع معتبر که پروکسی با پهنای باند واقعی برای ایران می‌گذارند
    sources = [
        "https://t.me/s/FalconProxy",
        "https://t.me/s/ProxyMTProto_Tel",
        "https://t.me/s/TelMTProto",
        "https://t.me/s/iMTProto"
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
                    if clean_url not in raw_proxies:
                        raw_proxies.append(clean_url)
        except Exception as e:
            print(f"Error fetching from {url}: {e}")

    # فیلتر هوشمند: فقط پروکسی‌هایی که Fake TLS هستند (دانلود و آپلود واقعی دارند)
    fast_proxies = []
    for p in raw_proxies:
        parsed = urllib.parse.urlparse(p)
        params = urllib.parse.parse_qs(parsed.query)
        secret = params.get("secret", [""])[0]
        
        # پروکسی‌هایی که سکرت آنها با ee شروع می‌شود تکنولوژی ضد مسدودسازی و دانلود روان دارند
        if secret.startswith("ee"):
            fast_proxies.append(p)

    # اگر پروکسی Fake TLS پیدا نشد، از بقیه موارد بردار تا چنل خالی نماند
    if not fast_proxies:
        fast_proxies = raw_proxies

    return fast_proxies

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
            print("Successfully sent high-speed proxies to channel!")
    except urllib.error.HTTPError as e:
        print(f"Failed to send: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is empty!")
        exit(1)
    
    proxies = get_high_speed_proxies()
    if proxies:
        selected_3 = proxies[-3:] if len(proxies) >= 3 else proxies
        send_to_channel(selected_3)
    else:
        print("No proxies found.")
