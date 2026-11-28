import os
import re
import socket
import time
import html
import base64
import urllib.request
import urllib.parse
import json

BOT_TOKEN = os.environ.get("BOT_TOKEN", "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y")
VIP_CHANNEL_ID = "-1005629553208"
SUB_FILE = "sub.txt"

SOURCES = [
    "https://t.me/s/v2rayngvpn",
    "https://t.me/s/V2rayEnglish",
    "https://t.me/s/MiTiVPN"
]

def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Fetch failed for {url}: {e}")
        return ""

def extract_configs_from_html(raw_html):
    clean_html = html.unescape(raw_html)
    configs = []
    for proto in ["vless://", "vmess://", "trojan://"]:
        matches = re.findall(rf"({proto}[^\s<\"']+)", clean_html)
        for m in matches:
            c = m.strip().replace("&amp;", "&")
            if len(c) > 30:
                configs.append(c)
    return configs

def ping_test(host, port, timeout=2.5):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start_time = time.time()
        sock.connect((host, port))
        latency = (time.time() - start_time) * 1000
        sock.close()
        return round(latency, 2)
    except Exception:
        return 9999

def parse_and_test(config_str):
    try:
        if config_str.startswith("vless://") or config_str.startswith("trojan://"):
            main_part = config_str.split("://")[1].split("#")[0].split("?")[0]
            host_port = main_part.split("@")[-1]
            host, port_str = host_port.split(":")
            return ping_test(host, int(port_str))
        elif config_str.startswith("vmess://"):
            b64_str = config_str.split("://")[1].split("#")[0]
            padding = len(b64_str) % 4
            if padding:
                b64_str += "=" * (4 - padding)
            data = json.loads(base64.b64decode(b64_str).decode("utf-8", errors="ignore"))
            return ping_test(data.get("add"), int(data.get("port", 443)))
    except Exception:
        pass
    return 9999

def brand_config(config_str, tag):
    clean_tag = urllib.parse.quote(f"Caspian-{tag} ⚡️ @proxy_caspian")
    base = config_str.split("#")[0]
    return f"{base}#{clean_tag}"

def escape_for_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def post_vip_message(v1, v2, n1, n2, t1, t2):
    message_text = (
        "👑 <b>کانفیگ اختصاصی اعضای VIP کاسپین</b> 👑\n\n"
        "♨️ <b>کانفیگ‌های پرسرعت و تست‌شده اختصاصی:</b>\n"
        "💡 <i>کافیست روی هر کادر ضربه بزنید تا کانفیگ فوراً کپی شود.</i>\n\n"
        "🔹 <b>کانفیگ‌های مخصوص V2Ray:</b>\n\n"
        f"▫️ سرور ۱ (پینگ فوق‌العاده):\n<code>{escape_for_html(v1)}</code>\n\n"
        f"▫️ سرور ۲ (پایدار و بدون قطعی):\n<code>{escape_for_html(v2)}</code>\n\n"
        "🔹 <b>کانفیگ‌های مخصوص NPV Tunnel:</b>\n\n"
        f"▫️ سرور ۱ (اتصال سریع):\n<code>{escape_for_html(n1)}</code>\n\n"
        f"▫️ سرور ۲ (همراه اول و ایرانسل):\n<code>{escape_for_html(n2)}</code>\n\n"
        "🔹 <b>کانفیگ‌های سوپر توربو (دوکاره):</b>\n\n"
        f"▫️ سرور توربو ۱ ⚡️:\n<code>{escape_for_html(t1)}</code>\n\n"
        f"▫️ سرور توربو ۲ ⚡️:\n<code>{escape_for_html(t2)}</code>\n\n"
        "📶 <b>مناسب برای:</b> همراه اول، ایرانسل، رایتل و مخابرات 📊\n"
        "🆔 @proxy_caspian"
    )

    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": VIP_CHANNEL_ID,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        req = urllib.request.Request(
            send_url,
            data=urllib.parse.urlencode(payload).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            print("VIP message posted successfully!")
    except Exception as e:
        print(f"Failed to post VIP message: {e}")

def main():
    print("Scraping Caspian VIP channels...")
    all_raw = []
    for src in SOURCES:
        html_data = fetch_url(src)
        configs = extract_configs_from_html(html_data)
        all_raw.extend(configs)

    unique_configs = list(set(all_raw))
    if not unique_configs:
        print("No configs extracted.")
        return

    tested = []
    for c in unique_configs:
        lat = parse_and_test(c)
        if lat < 9999:
            tested.append((lat, c))

    tested.sort(key=lambda x: x[0])
    valid_configs = [c for lat, c in tested] if tested else unique_configs

    v2ray_list = [c for c in valid_configs if c.startswith("vless://") or c.startswith("vmess://")]
    npv_list = [c for c in valid_configs if c.startswith("trojan://") or c.startswith("vless://")]

    c_v1 = brand_config(v2ray_list[0], "V2Ray-1") if len(v2ray_list) > 0 else brand_config(valid_configs[0], "V2Ray-1")
    c_v2 = brand_config(v2ray_list[1], "V2Ray-2") if len(v2ray_list) > 1 else brand_config(valid_configs[1 % len(valid_configs)], "V2Ray-2")

    c_n1 = brand_config(npv_list[0], "NPV-1") if len(npv_list) > 0 else brand_config(valid_configs[0], "NPV-1")
    c_n2 = brand_config(npv_list[1], "NPV-2") if len(npv_list) > 1 else brand_config(valid_configs[1 % len(valid_configs)], "NPV-2")

    c_t1 = brand_config(valid_configs[0], "Turbo-1")
    c_t2 = brand_config(valid_configs[1 % len(valid_configs)], "Turbo-2")

    # انتشار پست کامل در کانال VIP
    post_vip_message(c_v1, c_v2, c_n1, c_n2, c_t1, c_t2)

    # ساخت ساب‌اسکریپشن ۷ تایی برای اتصال خودکار
    sub_7 = [c_v1, c_v2, c_n1, c_n2, c_t1, c_t2]
    if len(valid_configs) > 2:
        sub_7.append(brand_config(valid_configs[2], "Backup"))
    else:
        sub_7.append(c_t1)

    with open(SUB_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sub_7) + "\n")
    print("Wrote exactly 7 configs to sub.txt successfully.")

if __name__ == "__main__":
    main()
