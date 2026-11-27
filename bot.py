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

# ۴ کانال اصلی VIP
VIP_CHANNELS = ["TelMTProto", "DarkProxy", "irproxy", "ProxyNP"]

# ۲ کانال زاپاس (پشتیبان کیفیت و قطعی)
BACKUP_CHANNELS = ["P1000Y", "ProxyDotNet"]

def fetch_channel_proxies(username):
    """استخراج لینک‌های پروکسی از پیش‌نمایش وب کانال"""
    url = f"https://t.me/s/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    found = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r'href="(https://t\.me/proxy\?[^"]+)"', html)
            for m in reversed(matches):
                clean = m.replace("&amp;", "&")
                if clean not in found:
                    found.append(clean)
    except Exception as e:
        print(f"خطا در خواندن کانال @{username}: {e}")
    return found

def test_proxy_speed(proxy_url):
    """تست پاسخ‌دهی سوکت، محاسبه پینگ و بررسی Fake TLS"""
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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.75) # تست سریع در کمتر از ۱ ثانیه
        result = sock.connect_ex((server, port_num))
        sock.close()

        if result == 0:
            ping_ms = int((time.time() - start_time) * 1000)
            is_faketls = secret.startswith("ee")
            
            # امتیازدهی: پروکسی‌های فیک‌تی‌ال‌اس پینگ واقعی دارن؛ بقیه جریمه سنگین میشن
            score = ping_ms if is_faketls else (ping_ms + 1500)

            # کیفیت خوب: پینگ معقول و حتماً سالم
            is_high_quality = is_faketls and (ping_ms < 600)

            return {
                "url": proxy_url,
                "server": server,
                "port": port,
                "ping": ping_ms,
                "is_faketls": is_faketls,
                "is_high_quality": is_high_quality,
                "score": score
            }
    except:
        pass
    return None

def analyze_and_rank(proxies_list):
    """تست همزمان پروکسی‌ها و مرتب‌سازی از سریع‌ترین به کندترین"""
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        checked = executor.map(test_proxy_speed, proxies_list)
        for c in checked:
            if c is not None:
                results.append(c)
    results.sort(key=lambda x: x["score"])
    return results

def get_top_unique_proxies():
    """
    منطق دو لایه:
    ۱. بررسی ۴ کانال اصلی
    ۲. در صورت نبودن، خرابی، یا بی‌کیفیت بودن پروکسی‌ها -> ورود خودکار کانال‌های زاپاس
    """
    vip_pool = []
    for ch in VIP_CHANNELS:
        vip_pool.extend(fetch_channel_proxies(ch))

    ranked_vip = analyze_and_rank(vip_pool)

    final_picks = []
    seen_servers = set()

    # پروکسی‌های باکیفیت و سریع کانال‌های اصلی را گلچین کن
    for p in ranked_vip:
        if p["is_high_quality"] and p["server"] not in seen_servers:
            final_picks.append(p)
            seen_servers.add(p["server"])
            if len(final_picks) == 4:
                break

    # اگر به هر دلیلی (خرابی، کار نکردن، یا بی‌کیفیت بودن) به ۴ تا نرسیدیم، زاپاس‌ها میان وسط
    if len(final_picks) < 4:
        print(f"تعداد پروکسی‌های باکیفیت اصلی ({len(final_picks)}) کم بود؛ فعال‌سازی کانال‌های زاپاس...")
        backup_pool = []
        for b_ch in BACKUP_CHANNELS:
            backup_pool.extend(fetch_channel_proxies(b_ch))
        
        ranked_backup = analyze_and_rank(backup_pool)
        for p in ranked_backup:
            if p["server"] not in seen_servers:
                final_picks.append(p)
                seen_servers.add(p["server"])
                if len(final_picks) == 4:
                    break

    # اگر باز هم کانال‌های زاپاس نتونستن پر کنن، از بهترین‌های باقی‌مانده عادی استفاده کن
    if len(final_picks) < 4:
        for p in ranked_vip:
            if p["server"] not in seen_servers:
                final_picks.append(p)
                seen_servers.add(p["server"])
                if len(final_picks) == 4:
                    break

    # مرتب‌سازی نهایی بر اساس کمترین پینگ
    final_picks.sort(key=lambda x: x["score"])
    return final_picks

def send_to_channel(proxy_data):
    if not proxy_data:
        print("هیچ پروکسی سالمی پیدا نشد.")
        return

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

    p1 = proxy_data[0]["url"]
    p2 = proxy_data[1]["url"] if len(proxy_data) > 1 else p1
    p3 = proxy_data[2]["url"] if len(proxy_data) > 2 else p1
    p4 = proxy_data[3]["url"] if len(proxy_data) > 3 else p2

    # چیدمان ۲ در ۲ دکمه‌ها و دکمه عضویت
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
            print("پست با موفقیت با ۴ پروکسی سالم ارسال شد.")
    except Exception as e:
        print(f"خطا در ارسال به کانال: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("خطا: BOT_TOKEN تنظیم نشده است.")
        exit(1)
        
    selected_proxies = get_top_unique_proxies()
    if selected_proxies:
        send_to_channel(selected_proxies)
