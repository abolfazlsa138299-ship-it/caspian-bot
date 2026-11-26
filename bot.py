import os
import re
import json
import socket
import time
import urllib.request
import urllib.parse
import urllib.error
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@proxy_caspian")

def fetch_proxies_from_url(url):
    """دریافت لینک‌های خام پروکسی از کانال"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    proxies = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r'href="(https://t\.me/proxy\?[^"]+)"', html)
            for m in reversed(matches):
                clean_url = m.replace("&amp;", "&")
                if clean_url not in proxies:
                    proxies.append(clean_url)
    except Exception as e:
        print(f"Error reading {url}: {e}")
    return proxies

def check_single_proxy(proxy_url):
    """تست پینگ و برقراری ارتباط واقعی با سرور پروکسی"""
    parsed = urllib.parse.urlparse(proxy_url)
    params = urllib.parse.parse_qs(parsed.query)
    server = params.get("server", [None])[0]
    port = params.get("port", [None])[0]
    secret = params.get("secret", [""])[0]

    if not server or not port:
        return None

    try:
        port_num = int(port)
        start_time = time.time()
        
        # تست اتصال سوکت با مهلت پاسخ ۱.۵ ثانیه
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.5)
        result = sock.connect_ex((server, port_num))
        sock.close()

        if result == 0:
            ping_ms = int((time.time() - start_time) * 1000)
            is_faketls = secret.startswith("ee")
            return {
                "url": proxy_url,
                "server": server,
                "port": port,
                "ping": ping_ms,
                "is_faketls": is_faketls
            }
    except:
        pass
    return None

def test_and_filter_proxies(proxy_urls):
    """تست همزمان تمام پروکسی‌ها در چند ثانیه و رتبه‌بندی آنها"""
    working_proxies = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(check_single_proxy, proxy_urls)
        for r in results:
            if r is not None:
                working_proxies.append(r)

    # مرتب‌سازی: اول پروکسی‌های Fake TLS و سپس کمترین پینگ (بالاترین سرعت)
    working_proxies.sort(key=lambda x: (not x["is_faketls"], x["ping"]))
    return working_proxies

def get_the_best_4_proxies():
    print("--- شروع تحلیل هوشمند و تست پروکسی‌ها ---")
    
    # مرحله ۱: دریافت و تست پروکسی‌های کانال اصلی (VIP)
    vip_raw = fetch_proxies_from_url("https://t.me/s/P1000Y")
    print(f"تعداد پروکسی‌های خام دریافتی از VIP: {len(vip_raw)}")
    
    vip_alive = test_and_filter_proxies(vip_raw)
    print(f"تعداد پروکسی‌های ۱۰۰٪ سالم و پرسرعت VIP: {len(vip_alive)}")

    selected = []
    
    # اضافه کردن بهترین پروکسی‌های سالم VIP
    for p in vip_alive:
        selected.append(p)
        if len(selected) == 4:
            break

    # مرحله ۲: اگر سالم‌های VIP کمتر از ۴ تا بود (یا غایب بود)، جایگزینی آنی از زاپاس
    needed = 4 - len(selected)
    if needed > 0:
        print(f"کمبود {needed} پروکسی! سوئیچ خودکار به زاپاس (@TelMTProto)...")
        backup_raw = fetch_proxies_from_url("https://t.me/s/TelMTProto")
        backup_alive = test_and_filter_proxies(backup_raw)
        print(f"پروکسی‌های سالم پیدا شده در زاپاس: {len(backup_alive)}")

        for p in backup_alive:
            # جلوگیری از پروکسی تکراری
            if not any(x["url"] == p["url"] for x in selected):
                selected.append(p)
                if len(selected) == 4:
                    break

    return selected

def send_to_channel(proxy_data_list):
    if not proxy_data_list:
        print("هیچ پروکسی سالمی در این لحظه یافت نشد.")
        return

    # مشخصات سرور اولین پروکسی منتخب
    server = proxy_data_list[0]["server"]
    port = proxy_data_list[0]["port"]

    caption = (
        "⚡️ <b>پروکسی کاسپین | PROXY</b>\n\n"
        "⚡️ <b>پروکسی پرسرعت و ضدفیلتر Caspian</b>\n"
        f"📡 سرور: <code>{server}</code>\n"
        f"🔌 پورت: <code>{port}</code>\n"
        "📶 مخصوص: همراه اول، ایرانسل و رایتل ⚡️\n\n"
        "🤍 با فوروارد کردن از ما حمایت کنید\n"
        "🆔 @proxy_caspian"
    )

    p1 = proxy_data_list[0]["url"]
    p2 = proxy_data_list[1]["url"] if len(proxy_data_list) > 1 else p1
    p3 = proxy_data_list[2]["url"] if len(proxy_data_list) > 2 else p1
    p4 = proxy_data_list[3]["url"] if len(proxy_data_list) > 3 else p2

    keyboard_layout = [
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
            print("۴ پروکسی تست‌شده و کاملاً سالم با موفقیت به کانال ارسال شدند!")
    except urllib.error.HTTPError as e:
        print(f"Failed to send: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("BOT_TOKEN is empty!")
        exit(1)
    
    best_proxies = get_the_best_4_proxies()
    if best_proxies:
        send_to_channel(best_proxies)
    else:
        print("خطا: هیچ پروکسی سالمی تایید نشد.")
