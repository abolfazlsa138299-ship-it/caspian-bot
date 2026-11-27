import base64
import html
import json
import os
import re
import socket
import time
import urllib.parse
import urllib.request

BOT_TOKEN = "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y"
VIP_CHANNEL_ID = "-1005629553208"

# فقط و فقط دو کانال مرجع اصلی شما
CHANNEL_V2RAY = "https://t.me/s/v2rayngvpn"
CHANNEL_NPV = "https://t.me/s/V2rayEnglish"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def parse_host_port(url_str: str):
    """استخراج هاست و پورت کانفیگ‌های VLESS و VMess و Trojan"""
    try:
        clean = url_str.strip()
        if clean.startswith("vmess://"):
            b64 = clean[8:].split("#")[0].strip()
            pad = 4 - (len(b64) % 4)
            if pad != 4:
                b64 += "=" * pad
            decoded = base64.b64decode(b64).decode("utf-8", errors="ignore")
            d = json.loads(decoded)
            return d.get("add"), int(d.get("port", 443))
        
        parsed = urllib.parse.urlsplit(clean)
        return parsed.hostname, int(parsed.port or 443)
    except Exception:
        return None, None


def test_latency(host: str, port: int, timeout: float = 1.3) -> float:
    """تست سلامت و پینگ واقعی سرور"""
    if not host or not port:
        return 9999.0
    try:
        start = time.time()
        with socket.create_connection((host, port), timeout=timeout):
            return round((time.time() - start) * 1000, 1)
    except Exception:
        return 9999.0


def fetch_url_content(url: str) -> str:
    """دریافت محتوای یک آدرس اینترنتی یا فایل"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def extract_configs_from_channel(channel_url: str) -> list:
    """اسکرپ کامل پست‌ها، متون و دانلود لینک فایل‌های داخل کانال"""
    configs = []
    html_content = fetch_url_content(channel_url)
    if not html_content:
        return configs

    # تمیزکاری کدهای HTML برای استخراج دقیق لینک‌ها
    decoded_html = html.unescape(html_content)

    # ۱. استخراج مستقیم کانفیگ‌ها از متن و کدهای پست‌ها
    found_direct = re.findall(r"(?:vless|vmess|trojan)://[^\s<>\"\'\n\r]+", decoded_html)
    configs.extend(found_direct)

    # ۲. بررسی لینک‌های فایل (مثلاً txt یا ساب‌اسکریپشن که در پست‌ها فرستاده شده)
    file_links = re.findall(r'href=[\'"](https?://[^\'"\s]+(?:\.txt|\.sub|raw|pastebin|telegra)[^\'"\s]*)[\'"]', decoded_html)
    for flink in file_links[:3]:  # بررسی ۳ فایل اخیر
        ftext = fetch_url_content(flink)
        if ftext:
            found_in_file = re.findall(r"(?:vless|vmess|trojan)://[^\s<>\"\'\n\r]+", ftext)
            configs.extend(found_in_file)

    # حذف تکراری‌ها و بازگرداندن تازه‌ترین‌ها
    return list(dict.fromkeys(reversed(configs)))


def clean_and_rename_config(config_str: str, index: int, label: str) -> str:
    """تغییر نام شکیل کانفیگ به برند کاسپین"""
    clean = config_str.strip()
    tag_name = f"Caspian-{label}-{index} ⚡ @proxy_caspian"
    
    if clean.startswith("vmess://"):
        try:
            b64 = clean[8:].split("#")[0].strip()
            pad = 4 - (len(b64) % 4)
            if pad != 4:
                b64 += "=" * pad
            decoded = base64.b64decode(b64).decode("utf-8", errors="ignore")
            d = json.loads(decoded)
            d["ps"] = tag_name
            new_b64 = base64.b64encode(json.dumps(d).encode("utf-8")).decode("utf-8")
            return f"vmess://{new_b64}"
        except Exception:
            return clean

    raw_config = clean.split("#")[0].strip()
    tag = urllib.parse.quote(tag_name)
    return f"{raw_config}#{tag}"


def filter_and_sort_by_ping(configs_list: list) -> list:
    """تست پینگ و مرتب‌سازی بر اساس کمترین پینگ"""
    tested = []
    for cfg in configs_list:
        host, port = parse_host_port(cfg)
        if host and port:
            ping = test_latency(host, port, timeout=1.3)
            if ping < 9999.0:
                tested.append((ping, cfg))
                if len(tested) >= 20:
                    break
    
    tested.sort(key=lambda x: x[0])
    return [item[1] for item in tested] if tested else configs_list[:10]


def send_telegram_vip_message(caption: str):
    """ارسال پست نهایی به کانال VIP"""
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": VIP_CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print("[+] پست با موفقیت به کانال VIP ارسال شد.")
    except Exception as e:
        print(f"[-] خطا در ارسال پیام به کانال VIP: {e}")


def main():
    print("[*] در حال اسکن کانال V2Ray (@v2rayngvpn)...")
    v2ray_raw = extract_configs_from_channel(CHANNEL_V2RAY)
    print(f"[+] تعداد {len(v2ray_raw)} کانفیگ از کانال V2Ray استخراج شد.")

    print("[*] در حال اسکن و بازگشایی فایل‌های کانال NPV (@V2rayEnglish)...")
    npv_raw = extract_configs_from_channel(CHANNEL_NPV)
    print(f"[+] تعداد {len(npv_raw)} کانفیگ از کانال NPV استخراج شد.")

    # تست پینگ و مرتب‌سازی کمترین تاخیر برای هر کانال جداگانه
    v2ray_sorted = filter_and_sort_by_ping(v2ray_raw)
    npv_sorted = filter_and_sort_by_ping(npv_raw)

    # انتخاب ۲ کانفیگ مخصوص V2Ray
    v2ray1 = clean_and_rename_config(v2ray_sorted[0], 1, "V2Ray")
    v2ray2 = clean_and_rename_config(v2ray_sorted[1], 2, "V2Ray")

    # انتخاب ۲ کانفیگ مخصوص NPV Tunnel
    npv_source = npv_sorted if len(npv_sorted) >= 2 else v2ray_sorted[2:]
    npv1 = clean_and_rename_config(npv_source[0], 1, "NPV")
    npv2 = clean_and_rename_config(npv_source[1], 2, "NPV")

    # انتخاب ۲ کانفیگ کم‌پینگ برای دوکاره (توربو) از ترکیب هر دو کانال
    combined_pool = v2ray_sorted[2:] + npv_source[2:]
    turbo_sorted = filter_and_sort_by_ping(combined_pool)
    if len(turbo_sorted) < 2:
        turbo_sorted = combined_pool if len(combined_pool) >= 2 else v2ray_sorted[:2]

    turbo1 = clean_and_rename_config(turbo_sorted[0], 1, "Turbo")
    turbo2 = clean_and_rename_config(turbo_sorted[1], 2, "Turbo")

    # متن شکیل VIP دقیقاً با قالب محبوب و اصیل
    caption = (
        "👑 <b>کانفیگ اختصاصی اعضای VIP کاسپین</b> 👑\n\n"
        "♨️ <b>کانفیگ‌های پرسرعت و تست‌شده اختصاصی:</b>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص V2Ray:</b></a>\n'
        f"1️⃣ <code>{html.escape(v2ray1)}</code>\n\n"
        f"2️⃣ <code>{html.escape(v2ray2)}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص NPV Tunnel:</b></a>\n'
        f"1️⃣ <code>{html.escape(npv1)}</code>\n\n"
        f"2️⃣ <code>{html.escape(npv2)}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های دوکاره (توربو):</b></a>\n'
        f"1️⃣ <code>{html.escape(turbo1)}</code>\n\n"
        f"2️⃣ <code>{html.escape(turbo2)}</code>\n\n"
        "📶 <b>مناسب برای:</b> همراه اول، ایرانسل، رایتل و مخابرات 📊\n"
        "💡 <b>راهنما:</b> فقط کافیه روی هر کانفیگ یکبار ضربه بزنید تا خودکار کپی شود."
    )

    send_telegram_vip_message(caption)

    # آپدیت ساب‌اسکریپشن با کانفیگ‌های هر دو کانال
    all_sub = [v2ray1, v2ray2, npv1, npv2, turbo1, turbo2] + [
        clean_and_rename_config(c, i, "VIP") for i, c in enumerate(v2ray_sorted[4:25], 3)
    ]
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(all_sub))

    print(f"[✓] فایل sub.txt و پست کانال VIP با موفقیت به روز شدند.")


if __name__ == "__main__":
    main()
