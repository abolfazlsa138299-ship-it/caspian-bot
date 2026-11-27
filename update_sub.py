import os
import json
import urllib.request
import re
import socket
import urllib.parse
import base64
import html
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y"
VIP_CHANNEL_ID = -1005629553208

# سورس‌های فعال ضد فیلتر
SOURCES_TG = [
    "meli_v2rayng",
    "v2ray_outlineir",
    "DailyV2RY",
    "yaney_01",
    "customv2ray"
]

RAW_SUBS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub6.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub2.txt"
]

def decode_sub(content):
    try:
        decoded = base64.b64decode(content.strip()).decode('utf-8', errors='ignore')
        return decoded.splitlines()
    except:
        return content.splitlines()

def fetch_fresh_configs():
    collected = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for sub_url in RAW_SUBS:
        try:
            req = urllib.request.Request(sub_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                text = resp.read().decode('utf-8', errors='ignore')
                lines = decode_sub(text)
                for line in lines:
                    line = line.strip()
                    if line.startswith("vless://") and ("reality" in line.lower() or "security=reality" in line.lower()):
                        collected.append(line)
        except Exception:
            pass

    for ch in SOURCES_TG:
        try:
            url = f"https://t.me/s/{ch}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                html_doc = resp.read().decode("utf-8", errors="ignore")
                matches = re.findall(r'(vless://[^\s<>"\'`]+|vmess://[^\s<>"\'`]+)', html_doc)
                for m in reversed(matches):
                    clean = html.unescape(m).replace("&amp;", "&")
                    if clean not in collected:
                        collected.append(clean)
        except Exception:
            pass

    return list(dict.fromkeys(collected))

def send_vip_post(cfgs):
    c1 = html.escape(cfgs[0].split("#")[0] + "#⚡️ Caspian | V2Ray 1")
    c2 = html.escape(cfgs[1].split("#")[0] + "#⚡️ Caspian | V2Ray 2")

    c3 = html.escape(cfgs[2].split("#")[0] + "#⚡️ Caspian | NPV 1")
    c4 = html.escape(cfgs[3].split("#")[0] + "#⚡️ Caspian | NPV 2")

    c5 = html.escape(cfgs[4].split("#")[0] + "#⚡️ Caspian | دوکاره 1")
    c6 = html.escape(cfgs[5].split("#")[0] + "#⚡️ Caspian | دوکاره 2")

    # عناوین با هایپرلینک به رنگ لینک‌های تلگرام درمی‌آیند
    caption = (
        "👑 <b>پست اختصاصی اعضای کاسپین VIP</b> 👑\n\n"
        "♨️ <b>کانفیگ‌های تازه‌نفس و ضد فیلتر کاسپین:</b>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص V2Ray:</b></a>\n'
        f"1️⃣ <code>{c1}</code>\n\n"
        f"2️⃣ <code>{c2}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های مخصوص NPV Tunnel:</b></a>\n'
        f"1️⃣ <code>{c3}</code>\n\n"
        f"2️⃣ <code>{c4}</code>\n\n"
        '🔹 <a href="https://t.me/proxy_caspian"><b>کانفیگ‌های دوکاره (توربو):</b></a>\n'
        f"1️⃣ <code>{c5}</code>\n\n"
        f"2️⃣ <code>{c6}</code>\n\n"
        "📶 <b>مناسب برای:</b> همراه اول، ایرانسل، رایتل و مخابرات 📊\n"
        "💡 <b>راهنما:</b> روی هر کانفیگ یکبار ضربه بزنید تا خودکار کپی شود."
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": VIP_CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            print("پست VIP با عناوین رنگی ارسال شد.")
    except Exception as e:
        print(f"خطا در ارسال: {e}")

def main():
    configs = fetch_fresh_configs()
    if len(configs) >= 6:
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(configs[:15]))
        send_vip_post(configs[:6])

if __name__ == "__main__":
    main()
