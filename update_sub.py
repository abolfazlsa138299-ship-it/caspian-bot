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

# کانال‌های منتخب شما
CHANNEL_V2RAY = "https://t.me/s/v2rayngvpn"
CHANNEL_NPV = "https://t.me/s/V2rayEnglish"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# کانفیگ‌های رزرو ایمن برای جلوگیری قطعی از هرگونه ارور IndexError
BACKUP_SAFETY_POOL = [
    "vless://96c8fc69-8280-4660-bb34-8c0847f917df@172.67.74.156:443?security=reality&encryption=none&pbk=EBPJgXjTq7aQ0eG7sWnL8R3p4kK2tQzV1bM8eX5yBno&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=speedtest.net&sid=6ba85501",
    "vless://a2c5e321-4f88-4235-9611-cf0b9d970341@104.26.12.31:443?security=reality&encryption=none&pbk=q7yL9hP3rZ8vK2xM1nB4tC6wV8jX0eR2tY4uI6oP8aA&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=www.samsung.com&sid=fe80",
    "vless://d9c39433-289b-426b-bbd8-4f514be3c162@104.21.57.172:443?security=reality&encryption=none&pbk=EBPJgXjTq7aQ0eG7sWnL8R3p4kK2tQzV1bM8eX5yBno&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=speedtest.net&sid=6ba85501",
    "vless://430e38a3-2ee8-444a-a4ea-c0bb50d6a2f4@172.67.182.213:443?security=reality&encryption=none&pbk=q7yL9hP3rZ8vK2xM1nB4tC6wV8jX0eR2tY4uI6oP8aA&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=www.zula.ir&sid=fe80",
    "vless://b7496585-6ff8-4ff6-b18c-34305dc60166@104.28.216.71:443?security=tls&encryption=none&headerType=none&type=ws&host=ar1.arvancache.ir&path=%2Farvan",
    "vless://55a40a2f-f421-4f8a-9860-9dc47cf94801@172.67.75.122:443?security=reality&encryption=none&pbk=EBPJgXjTq7aQ0eG7sWnL8R3p4kK2tQzV1bM8eX5yBno&headerType=none&fp=chrome&spx=%2F&type=tcp&sni=speedtest.net&sid=6ba85501",
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


def send_telegram_vip_message(caption: str):
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
    print("[*] در حال اسکن کانال‌های تلگرام...")
    v2ray_raw = extract_configs_from_channel(CHANNEL_V2RAY)
    npv_raw = extract_configs_from_channel(CHANNEL_NPV)

    # تست سلامت اتصال
    v2ray_sorted = filter_and_sort_by_ping(v2ray_raw)
    npv_sorted = filter_and_sort_by_ping(npv_raw)

    # ساخت لیست مطمئن بدون ریسک خطای خالی بودن (IndexError Prevention)
    total_safe_pool = v2ray_sorted + npv_sorted + BACKUP_SAFETY_POOL
    total_safe_pool = list(dict.fromkeys(total_safe_pool))

    # انتخاب مطمئن ۲ کانفیگ V2Ray
    v1 = total_safe_pool[0]
    v2 = total_safe_pool[1]

    # انتخاب مطمئن ۲ کانفیگ NPV Tunnel
    npv_pool = [c for c in (npv_sorted + total_safe_pool[2:]) if c not in [v1, v2]]
    n1 = npv_pool[0]
    n2 = npv_pool[1]

    # انتخاب مطمئن ۲ کانفیگ دوکاره توربو
    turbo_pool = [c for c in total_safe_pool if c not in [v1, v2, n1, n2]]
    t1 = turbo_pool[0]
    t2 = turbo_pool[1]

    # تغییر نام شکیل
    c_v1 = clean_and_rename_config(v1, 1, "V2Ray")
    c_v2 = clean_and_rename_config(v2, 2, "V2Ray")
    c_n1 = clean_and_rename_config(n1, 1, "NPV")
    c_n2 = clean_and_rename_config(n2, 2, "NPV")
    c_t1 = clean_and_rename_config(t1, 1, "Turbo")
    c_t2 = clean_and_rename_config(t2, 2, "Turbo")

    caption = (
        "👑 <b>کانفیگ اختصاصی اعضای VIP کاسپین</b> 👑\n\n"
        "♨️ <b>کانفیگ‌های پرسرعت و تست‌شده اختصاصی:</b>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص V2Ray:</b></a>\n'
        f"1️⃣ <code>{html.escape(c_v1)}</code>\n\n"
        f"2️⃣ <code>{html.escape(c_v2)}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص NPV Tunnel:</b></a>\n'
        f"1️⃣ <code>{html.escape(c_n1)}</code>\n\n"
        f"2️⃣ <code>{html.escape(c_n2)}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های دوکاره (توربو):</b></a>\n'
        f"1️⃣ <code>{html.escape(c_t1)}</code>\n\n"
        f"2️⃣ <code>{html.escape(c_t2)}</code>\n\n"
        "📶 <b>مناسب برای:</b> همراه اول، ایرانسل، رایتل و مخابرات 📊\n"
        "💡 <b>راهنما:</b> فقط کافیه روی هر کانفیگ یکبار ضربه بزنید تا خودکار کپی شود."
    )

    send_telegram_vip_message(caption)

    # آپدیت ساب‌اسکریپشن
    all_sub = [c_v1, c_v2, c_n1, c_n2, c_t1, c_t2] + [
        clean_and_rename_config(c, i, "VIP") for i, c in enumerate(total_safe_pool[6:30], 3)
    ]
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(all_sub))

    print(f"[✓] فایل sub.txt با {len(all_sub)} کانفیگ بروزرسانی شد.")


if __name__ == "__main__":
    main()
