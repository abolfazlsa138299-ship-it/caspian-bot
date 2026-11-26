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

def fetch_raw_proxies(url):
    """استخراج لینک‌های پروکسی از کانال"""
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
        print(f"Error fetching from {url}: {e}")
    return proxies

def evaluate_proxy(proxy_url):
    """تست پینگ دقیق و بررسی فناوری ضد فیلتر"""
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
        
        # تست اتصال مستقیم سوکت با مهلت پاسخ ۱.۲ ثانیه برای فیلتر کردن سرورهای کند
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.2)
        result = sock.connect_ex((server, port_num))
        sock.close()

        if result == 0:
            ping_ms = int((time.time() - start_time) * 1000)
            is_faketls = secret.startswith("ee")
            
            # امتیازدهی: Fake TLS اولویت اول است و سپس پینگ کمتر
            score = ping_ms if is_faketls else (ping_ms + 1000)
            
            return {
                "url": proxy_url,
                "server": server,
                "port": port,
                "ping": ping_ms,
                "is_faketls": is_faketls,
                "score": score
            }
    except:
        pass
    return None

def test_and_rank(proxies_list):
    """تست همزمان چند نخی (Multi-Thread) و رتبه‌بندی کیفی"""
    tested = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        results = executor.map(evaluate_proxy, proxies_list)
        for r in results:
            if r is not None:
                tested.append(r)
                
    # مرتب‌سازی: بهترین و سریع‌ترین‌ها در ابتدای لیست قرار می‌گیرند
    tested.sort(key=lambda x: x["score"])
    return tested

def select_top_4_proxies():
    print("--- بررسی و غربالگری هوشمند پروکسی‌ها ---")
    
    # منبع اول (VIP): TelMTProto
    vip_proxies = fetch_raw_proxies("https://t.me/s/TelMTProto")
    print(f"پروکسی‌های دریافتی از منبع اصلی: {len(vip_proxies)}")
    ranked_vip = test_and_rank(vip_proxies)
    print(f"پروکسی‌های فعال و تایید شده اصلی: {len(ranked_vip)}")

    final_selection = []
    
    # گلچین کردن بهترین‌ها از منبع اصلی
    for p in ranked_vip:
        final_selection.append(p)
        if len(final_selection) == 4:
            break

    # در صورت کمبود، سوئیچ آنی به زاپاس (P1000Y)
    needed = 4 - len(final_selection)
    if needed > 0:
        print(f"نیاز به {needed} پروکسی مکمل! دریافت از منبع زاپاس (@P1000Y)...")
        backup_proxies = fetch_raw_proxies("https://t.me/s/P1000Y")
        ranked_backup = test_and_rank(backup_proxies)
        print(f"پروکسی‌های فعال زاپاس: {len(ranked_backup)}")

        for p in ranked_backup:
            if not any(item["url"] == p["url"] for item in final_selection):
                final_selection.append(p)
                if len(final_selection) == 4:
                    break

    # مرتب‌سازی نهایی برای تضمین اینکه دکمه ۱ و ۲ بهترین‌ها باشند
    final_selection.sort(key=lambda x: x["score"])
    return final_selection

def send_to_channel(proxy_data):
    if not proxy_data:
        print("هیچ پروکسی فعالی برای ارسال یافت نشد.")
        return

    # مشخصات سرور بهترین پروکسی (رتبه اول)
    best_server = proxy_data[0]["server"]
    best_port = proxy_data[0]["port"]

    caption = (
        "⚡️ <b>پروکسی کاسپین | PROXY</b>\n\n"
        "⚡️ <b>پروکسی پرسرعت و ضدفیلتر Caspian</b>\n"
        f"📡 سرور: <code>{best_server}</code>\n"
        f"🔌 پورت: <code>{best_port}</code>\n"
        "📶 مخصوص: همراه اول، ایرانسل و رایتل ⚡️\n\n"
        "🤍 با فوروارد کردن از ما حمایت کنید\n"
        "🆔 @proxy_caspian"
    )

    # چیدمان ۲×۲ (دکمه‌های ۱ و ۲ دقیقاً سریع‌ترین و کم‌پینگ‌ترین پروکسی‌ها هستند)
    p1 = proxy_data[0]["url"]
    p2 = proxy_data[1]["url"] if len(proxy_data) > 1 else p1
    p3 = proxy_data[2]["url"] if len(proxy_data) > 2 else p1
    p4 = proxy_data[3]["url"] if len(proxy_data) > 3 else p2

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
            print("پست ۴ تایی با موفقیت ارسال شد.")
    except urllib.error.HTTPError as e:
        print(f"Failed to send: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("BOT_TOKEN is empty!")
        exit(1)
    
    best_4 = select_top_4_proxies()
    if best_4:
        send_to_channel(best_4)
    else:
        print("خطا: هیچ پروکسی فعالی از هر دو منبع تایید نشد.")
