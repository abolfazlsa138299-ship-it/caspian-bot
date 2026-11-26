import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@proxy_caspian")

def extract_fresh_proxies(channel_username):
    """استخراج جدیدترین پروکسی‌های منتشر شده در ساعات اخیر"""
    url = f"https://t.me/s/{channel_username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    found_proxies = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r'href="(https://t\.me/proxy\?[^"]+)"', html)
            
            # خواندن از آخرین پیام‌ها (جدیدترین‌ها) به سمت عقب
            for m in reversed(matches):
                clean_url = m.replace("&amp;", "&")
                if clean_url not in found_proxies:
                    found_proxies.append(clean_url)
    except Exception as e:
        print(f"Error fetching @{channel_username}: {e}")
        
    return found_proxies

def rank_and_pick_best(proxy_list):
    """تفکیک هوشمند: پروکسی‌های عالی و پرسرعت برای دکمه ۱ و ۲"""
    tier_1 = [] # پروکسی‌های Fake TLS فوق سریع با پورت ۴۴۳
    tier_2 = [] # پروکسی‌های Fake TLS معمولی
    tier_3 = [] # سایر پروکسی‌ها

    for p in proxy_list:
        parsed = urllib.parse.urlparse(p)
        params = urllib.parse.parse_qs(parsed.query)
        port = params.get("port", [""])[0]
        secret = params.get("secret", [""])[0]

        # اولویت طلایی: سکرت ee + پورت 443 یا 8443
        if secret.startswith("ee") and port in ["443", "8443"]:
            tier_1.append(p)
        elif secret.startswith("ee") or secret.startswith("7"):
            tier_2.append(p)
        else:
            tier_3.append(p)

    # ترکیب بر اساس اولویت کیفیت (بهترین‌ها همیشه اول قرار می‌گیرند)
    sorted_proxies = tier_1 + tier_2 + tier_3
    return sorted_proxies

def get_slot_proxies():
    print("--- دریافت و تفکیک پروکسی‌های تازه و فعال ---")
    
    # اولویت اول: کانال اصلی TelMTProto
    main_proxies = extract_fresh_proxies("TelMTProto")
    ranked_main = rank_and_pick_best(main_proxies)
    print(f"تعداد پروکسی‌های تازه از منبع اصلی: {len(ranked_main)}")

    final_selection = []
    
    # گلچین تاپ‌ترین‌های منبع اصلی
    for p in ranked_main:
        final_selection.append(p)
        if len(final_selection) == 4:
            break

    # اگر منبع اصلی پروکسی کافی نداشت (یا در آن شیفت پست نگذاشته بود)، دریافت از زاپاس
    needed = 4 - len(final_selection)
    if needed > 0:
        print(f"پست‌های منبع اصلی ناکافی بود. سوئیچ به زاپاس (@P1000Y)...")
        backup_proxies = extract_fresh_proxies("P1000Y")
        ranked_backup = rank_and_pick_best(backup_proxies)
        print(f"تعداد پروکسی‌های دریافتی از زاپاس: {len(ranked_backup)}")

        for p in ranked_backup:
            if p not in final_selection:
                final_selection.append(p)
                if len(final_selection) == 4:
                    break

    return final_selection

def send_to_channel(proxy_list):
    if not proxy_list:
        print("هیچ پروکسی تازه‌ای پیدا نشد.")
        return

    # استخراج سرور و پورت پروکسی اول (بهترین پروکسی)
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

    # چیدمان ۲×۲: دکمه ۱ و ۲ بهترین‌های مطلق هستند
    p1 = proxy_list[0]
    p2 = proxy_list[1] if len(proxy_list) > 1 else p1
    p3 = proxy_list[2] if len(proxy_list) > 2 else p1
    p4 = proxy_list[3] if len(proxy_list) > 3 else p2

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
    
    best_proxies = get_slot_proxies()
    if best_proxies:
        send_to_channel(best_proxies)
    else:
        print("خطا: پروکسی جدیدی یافت نشد.")
