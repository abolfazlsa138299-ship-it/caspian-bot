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

# دو کانال مرجع
CHANNEL_V2RAY = "https://t.me/s/v2rayngvpn"
CHANNEL_NPV = "https://t.me/s/V2rayEnglish"

# آدرس سرور هدایت‌کننده اختصاصی کاسپین
REDIRECT_BASE = "https://caspian-bot-c0b6.onrender.com/c?url="

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

BACKUP_NPV_POOL = [
    "vless://96c8fc69-8280-4660-bb34-8c0847f917df@172.67.74.156:443?security=reality&encryption=none&pbk=EBPJgXjTq7aQ0eG7sWnL8R3p4kK2tQzV1bM8eX5yBno&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=speedtest.net&sid=6ba85501",
    "vless://a2c5e321-4f88-4235-9611-cf0b9d970341@104.26.12.31:443?security=reality&encryption=none&pbk=q7yL9hP3rZ8vK2xM1nB4tC6wV8jX0eR2tY4uI6oP8aA&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=www.samsung.com&sid=fe80",
    "vless://d9c39433-289b-426b-bbd8-4f514be3c162@104.21.57.172:443?security=reality&encryption=none&pbk=EBPJgXjTq7aQ0eG7sWnL8R3p4kK2tQzV1bM8eX5yBno&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=speedtest.net&sid=6ba85501",
    "vless://430e38a3-2ee8-444a-a4ea-c0bb50d6a2f4@172.67.182.213:443?security=reality&encryption=none&pbk=q7yL9hP3rZ8vK2xM1nB4tC6wV8jX0eR2tY4uI6oP8aA&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=www.zula.ir&sid=fe80",
    "vless://b7496585-6ff8-4ff6-b18c-34305dc60166@104.28.216.71:443?security=tls&encryption=none&headerType=none&type=ws&host=ar1.arvancache.ir&path=%2Farvan",
    "vless://55a40a2f-f421-4f8a-9860-9dc47cf94801@172.67.75.122:443?security=reality&encryption=none&pbk=EBPJgXjTq7aQ0eG7sWnL8R3p4kK2tQzV1bM8eX5yBno&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=speedtest.net&sid=6ba85501",
    "vless://e859b921-6548-4e89-a9c1-4b1548e65321@172.67.222.1:443?security=reality&encryption=none&pbk=EBPJgXjTq7aQ0eG7sWnL8R3p4kK2tQzV1bM8eX5yBno&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=speedtest.net&sid=6ba85501",
]


def parse_host_port(url_str: str):
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
    if not host or not port:
        return 9999.0
    try:
        start = time.time()
        with socket.create_connection((host, port), timeout=timeout):
            return round((time.time() - start) * 1000, 1)
    except Exception:
        return 9999.0


def fetch_url_content(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def extract_configs_from_channel(channel_url: str) -> list:
    configs = []
    html_content = fetch_url_content(channel_url)
    if not html_content:
        return configs

    decoded_html = html.unescape(html_content)
    found_direct = re.findall(r"(?:vless|vmess|trojan)://[^\s<>\"\'\n\r]+", decoded_html)
    configs.extend(found_direct)

    file_links = re.findall(r'href=[\'"](https?://[^\'"\s]+(?:\.txt|\.sub|raw|pastebin|telegra)[^\'"\s]*)[\'"]', decoded_html)
    for flink in file_links[:3]:
        ftext = fetch_url_content(flink)
        if ftext:
            found_in_file = re.findall(r"(?:vless|vmess|trojan)://[^\s<>\"\'\n\r]+", ftext)
            configs.extend(found_in_file)

    return list(dict.fromkeys(reversed(configs)))


def clean_and_rename_config(config_str: str, index: int, label: str) -> str:
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
    return [item[1] for item in tested] if tested else configs_list


def send_telegram_vip_post(caption: str, reply_markup: dict):
    """ارسال پست همراه با دکمه‌های شیشه‌ای زیر هم"""
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": VIP_CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": json.dumps(reply_markup),
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print("[+] پست با موفقیت همراه با دکمه‌های کشیده به VIP ارسال شد.")
    except Exception as e:
        print(f"[-] خطا در ارسال: {e}")


def main():
    print("[*] در حال اسکن کانال‌های تلگرام...")
    v2ray_raw = extract_configs_from_channel(CHANNEL_V2RAY)
    npv_raw = extract_configs_from_channel(CHANNEL_NPV)

    v2ray_sorted = filter_and_sort_by_ping(v2ray_raw)
    npv_sorted = filter_and_sort_by_ping(npv_raw)

    safe_npv_pool = npv_sorted + BACKUP_NPV_POOL
    safe_npv_pool = list(dict.fromkeys(safe_npv_pool))

    # ۶ کانفیگ اختصاصی
    c_v1 = clean_and_rename_config(v2ray_sorted[0], 1, "V2Ray")
    c_v2 = clean_and_rename_config(v2ray_sorted[1], 2, "V2Ray")
    c_n1 = clean_and_rename_config(safe_npv_pool[0], 1, "NPV")
    c_n2 = clean_and_rename_config(safe_npv_pool[1], 2, "NPV")
    c_t1 = clean_and_rename_config(safe_npv_pool[2], 1, "Turbo")
    c_t2 = clean_and_rename_config(v2ray_sorted[2], 2, "Turbo")

    # متن فوق‌العاده شیک، تمیز و خلوت (بدون دیوارهای متنی زشت!)
    caption = (
        "👑 <b>کانفیگ اختصاصی اعضای VIP کاسپین</b> 👑\n\n"
        "♨️ <b>کانفیگ‌های پرسرعت و تست‌شده اختصاصی:</b>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص V2Ray:</b></a>\n'
        "▫️ سرور اختصاصی ۱ (پینگ فوق‌العاده)\n"
        "▫️ سرور اختصاصی ۲ (پایدار و بدون قطعی)\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص NPV Tunnel:</b></a>\n'
        "▫️ سرور اختصاصی ۱ (اتصال سریع)\n"
        "▫️ سرور اختصاصی ۲ (مخصوص همراه اول و ایرانسل)\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های دوکاره (توربو):</b></a>\n'
        "▫️ سرور سوپر توربو ۱ ⚡️\n"
        "▫️ سرور سوپر توربو ۲ ⚡️\n\n"
        "📶 <b>مناسب برای:</b> همراه اول، ایرانسل، رایتل و مخابرات 📊\n"
        "💡 <b>راهنما:</b> کافیست روی هر کدام از دکمه‌های زیر ضربه بزنید تا مستقیماً در نرم‌افزار شما باز شود."
    )

    # چینش دکمه‌ها: دقیقاً تک‌تک، زیر هم و با عرض کامل (کشیده)
    keyboard = {
        "inline_keyboard": [
            [{"text": "🚀 اتصال به سرور ۱ (V2Ray)", "url": REDIRECT_BASE + urllib.parse.quote(c_v1)}],
            [{"text": "🚀 اتصال به سرور ۲ (V2Ray)", "url": REDIRECT_BASE + urllib.parse.quote(c_v2)}],
            [{"text": "🛡 اتصال به سرور ۱ (NPV Tunnel)", "url": REDIRECT_BASE + urllib.parse.quote(c_n1)}],
            [{"text": "🛡 اتصال به سرور ۲ (NPV Tunnel)", "url": REDIRECT_BASE + urllib.parse.quote(c_n2)}],
            [{"text": "⚡️ اتصال به سرور ۱ (دوکاره توربو)", "url": REDIRECT_BASE + urllib.parse.quote(c_t1)}],
            [{"text": "⚡️ اتصال به سرور ۲ (دوکاره توربو)", "url": REDIRECT_BASE + urllib.parse.quote(c_t2)}],
        ]
    }

    send_telegram_vip_post(caption, keyboard)

    # آماده‌سازی ۷ کانفیگ فایل ساب‌اسکریپشن NPV
    sub_7_configs = [
        clean_and_rename_config(safe_npv_pool[2], 1, "NPV-Turbo"),
        clean_and_rename_config(safe_npv_pool[0], 2, "NPV-VIP"),
        clean_and_rename_config(safe_npv_pool[1], 3, "NPV-VIP"),
        clean_and_rename_config(safe_npv_pool[3], 4, "NPV-Pro"),
        clean_and_rename_config(safe_npv_pool[4], 5, "NPV-Pro"),
        clean_and_rename_config(safe_npv_pool[5], 6, "NPV-Pro"),
        clean_and_rename_config(safe_npv_pool[6], 7, "NPV-Pro"),
    ]

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sub_7_configs))

    print(f"[✓] پست دکمه‌ای به کانال VIP رفت و فایل sub.txt با ۷ سرور طلایی ذخیره شد.")


if __name__ == "__main__":
    main()
