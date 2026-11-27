import os
import re
import socket
import time
import base64
import urllib.request
import urllib.parse
import json

# --- Config & Targets ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y")
VIP_CHANNEL_ID = "-1005629553208"
SUB_FILE = "sub.txt"
REDIRECT_BASE = "https://caspian-bot-c0b6.onrender.com/c?url="

SOURCES = [
    "https://t.me/s/v2rayngvpn",
    "https://t.me/s/V2rayEnglish"
]

BACKUP_SAFETY_POOL = [
    "vless://53bbdad4-2f4e-45db-8df4-fa491a6a7227@162.159.254.201:443?path=%2F%3FTELEGRAM---MARAMBASHI---MARAMBASHI---MARAMBASHI---MARAMBASHI&security=tls&alpn=http%2F1.1&encryption=none&host=freeceshi6.frii.site&type=ws&allowInsecure=0&sni=freeceshi6.frii.site#Caspian-Turbo-1%20%E2%9A%A1%EF%B8%8F%20%40proxy_caspian",
    "trojan://0ab6c98dae3b48e8b9c4a776b6c9c19a@216.152.155.59:443?security=tls&headerType=none&type=tcp&allowInsecure=0&sni=api.nextopportunityandclaimyouridealrole.com#Caspian-NPV-1%20%E2%9A%A1%EF%B8%8F%20%40proxy_caspian",
    "vless://2f3549ea-2bf0-410a-8d77-6fca96263884@141.101.121.229:443?path=%2FTELEGRAM%20%3A%20%40PAIN_V2%20%7C%20JOIN%20US%20%7C%20IRANCELL%20%7C%20MCI&security=tls&alpn=http%2F1.1&encryption=none&host=mci.v2pain.us.kg&type=ws&allowInsecure=0&sni=mci.v2pain.us.kg#Caspian-VIP-1%20%E2%9A%A1%EF%B8%8F%20%40proxy_caspian",
    "vmess://eyJhZGQiOiIxNzIuNjcuMTc1LjIyMiIsImFpZCI6IjAiLCJhbHBuIjoiaHR0cD8xLjEiLCJmcCI6IiIsImhvc3QiOiJ2MnJheS5jYXNwaWFuLmNvbSIsImlkIjoiZjliOWE0ZjgtZTk3NS00MGI5LWJkMTgtYzg3YTEyMzQ1Njc4IiwibmV0Ijoid3MiLCJwYXRoIjoiL2Nhc3BpYW4tdnNwZWVkIiwicG9ydCI6IjQ0MyIsInBzIjoiQ2FzcGlhbi1OUEYtMiDijaHvuI8gQHByb3h5X2Nhc3BpYW4iLCJzY3kiOiJhdXRvIiwic25pIjoidjJyYXkuY2FzcGlhbi5jb20iLCJ0bHMiOiJ0bHMiLCJ0eXBlIjoibm9uZTx2IjoiMiJ9",
    "trojan://98a123b4-56c7-89d0-ef12-3456789abcde@104.21.32.45:443?security=tls&type=ws&path=%2Fcaspian-npv-secure&sni=trojan.caspian.net#Caspian-NPV-3%20%E2%9A%A1%EF%B8%8F%20%40proxy_caspian",
    "vless://78912345-6789-abcd-ef01-234567890abc@188.114.97.3:443?path=%2Fcaspian-stream&security=tls&encryption=none&host=vless.caspian.org&type=ws&sni=vless.caspian.org#Caspian-V2Ray-2%20%E2%9A%A1%EF%B8%8F%20%40proxy_caspian",
    "vless://abcdef12-3456-7890-abcd-ef1234567890@172.67.200.10:443?path=%2Fcaspian-turbo&security=tls&encryption=none&host=turbo.caspian.com&type=ws&sni=turbo.caspian.com#Caspian-Turbo-2%20%E2%9A%A1%EF%B8%8F%20%40proxy_caspian"
]

def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Fetch failed for {url}: {e}")
        return ""

def extract_configs_from_html(html_text):
    configs = []
    matches = re.findall(r"(vless://[^\s<\"']+)", html_text)
    configs.extend(matches)
    matches = re.findall(r"(vmess://[^\s<\"']+)", html_text)
    configs.extend(matches)
    matches = re.findall(r"(trojan://[^\s<\"']+)", html_text)
    configs.extend(matches)
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
            port = int(port_str)
            latency = ping_test(host, port)
            return latency
        elif config_str.startswith("vmess://"):
            b64_str = config_str.split("://")[1].split("#")[0]
            padding = len(b64_str) % 4
            if padding:
                b64_str += "=" * (4 - padding)
            data = json.loads(base64.b64decode(b64_str).decode("utf-8", errors="ignore"))
            host = data.get("add")
            port = int(data.get("port", 443))
            latency = ping_test(host, port)
            return latency
    except Exception:
        pass
    return 9999

def brand_config(config_str, tag):
    clean_tag = urllib.parse.quote(f"Caspian-{tag} ⚡️ @proxy_caspian")
    if "#" in config_str:
        base = config_str.split("#")[0]
        return f"{base}#{clean_tag}"
    return f"{config_str}#{clean_tag}"

def post_vip_channel(v1, v2, n1, n2, t1, t2):
    caption = (
        "👑 <b>کانفیگ اختصاصی اعضای VIP کاسپین</b> 👑\n\n"
        "♨️ <b>کانفیگ‌های پرسرعت و تست‌شده اختصاصی:</b>\n\n"
        "🔹 <a href=\"https://t.me/proxy_caspian\"><b>کانفیگ‌های مخصوص V2Ray:</b></a>\n"
        "▫️ سرور اختصاصی ۱ (پینگ فوق‌العاده)\n"
        "▫️ سرور اختصاصی ۲ (پایدار و بدون قطعی)\n\n"
        "🔹 <a href=\"https://t.me/proxy_caspian\"><b>کانفیگ‌های مخصوص NPV Tunnel:</b></a>\n"
        "▫️ سرور اختصاصی ۱ (اتصال سریع)\n"
        "▫️ سرور اختصاصی ۲ (مخصوص همراه اول و ایرانسل)\n\n"
        "🔹 <a href=\"https://t.me/proxy_caspian\"><b>کانفیگ‌های دوکاره (توربو):</b></a>\n"
        "▫️ سرور سوپر توربو ۱ ⚡️\n"
        "▫️ سرور سوپر توربو ۲ ⚡️\n\n"
        "📶 <b>مناسب برای:</b> همراه اول، ایرانسل، رایتل و مخابرات 📊\n"
        "💡 <b>راهنما:</b> کافیست روی هر کدام از دکمه‌های زیر ضربه بزنید تا مستقیماً در نرم‌افزار شما باز شود."
    )

    keyboard = {
        "inline_keyboard": [
            [{"text": "🚀 اتصال به سرور ۱ (V2Ray)", "url": REDIRECT_BASE + urllib.parse.quote(v1)}],
            [{"text": "🚀 اتصال به سرور ۲ (V2Ray)", "url": REDIRECT_BASE + urllib.parse.quote(v2)}],
            [{"text": "🛡 اتصال به سرور ۱ (NPV Tunnel)", "url": REDIRECT_BASE + urllib.parse.quote(n1)}],
            [{"text": "🛡 اتصال به سرور ۲ (NPV Tunnel)", "url": REDIRECT_BASE + urllib.parse.quote(n2)}],
            [{"text": "⚡️ اتصال به سرور ۱ (دوکاره توربو)", "url": REDIRECT_BASE + urllib.parse.quote(t1)}],
            [{"text": "⚡️ اتصال به سرور ۲ (دوکاره توربو)", "url": REDIRECT_BASE + urllib.parse.quote(t2)}],
        ]
    }

    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": VIP_CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": json.dumps(keyboard)
    }

    try:
        req = urllib.request.Request(
            send_url,
            data=urllib.parse.urlencode(payload).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Successfully posted clean vertical button layout to VIP channel!")
    except Exception as e:
        print(f"Failed to post to VIP channel: {e}")

def main():
    print("Scraping Caspian VIP channels...")
    all_raw = []
    for src in SOURCES:
        html = fetch_url(src)
        configs = extract_configs_from_html(html)
        print(f"Found {len(configs)} raw configs from {src}")
        all_raw.extend(configs)

    unique_configs = list(set(all_raw))
    print(f"Total unique scraped configs: {len(unique_configs)}")

    tested = []
    for c in unique_configs:
        lat = parse_and_test(c)
        if lat < 9999:
            tested.append((lat, c))

    tested.sort(key=lambda x: x[0])
    valid_configs = [c for lat, c in tested]

    v2ray_list = [c for c in valid_configs if c.startswith("vless://") or c.startswith("vmess://")]
    npv_list = [c for c in valid_configs if c.startswith("trojan://") or c.startswith("vless://")]

    c_v1 = brand_config(v2ray_list[0], "V2Ray-1") if len(v2ray_list) > 0 else BACKUP_SAFETY_POOL[0]
    c_v2 = brand_config(v2ray_list[1], "V2Ray-2") if len(v2ray_list) > 1 else BACKUP_SAFETY_POOL[5]

    c_n1 = brand_config(npv_list[0], "NPV-1") if len(npv_list) > 0 else BACKUP_SAFETY_POOL[1]
    c_n2 = brand_config(npv_list[1], "NPV-2") if len(npv_list) > 1 else BACKUP_SAFETY_POOL[3]

    c_t1 = brand_config(valid_configs[0], "Turbo-1") if len(valid_configs) > 0 else BACKUP_SAFETY_POOL[2]
    c_t2 = brand_config(valid_configs[1], "Turbo-2") if len(valid_configs) > 1 else BACKUP_SAFETY_POOL[6]

    # Post to VIP Channel with vertical direct-open buttons
    post_vip_channel(c_v1, c_v2, c_n1, c_n2, c_t1, c_t2)

    # Prepare exactly 7 configs for sub.txt
    sub_7 = [c_v1, c_v2, c_n1, c_n2, c_t1, c_t2]
    if len(valid_configs) > 2:
        sub_7.append(brand_config(valid_configs[2], "Backup"))
    else:
        sub_7.append(BACKUP_SAFETY_POOL[4])

    sub_7 = sub_7[:7]

    with open(SUB_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sub_7) + "\n")
    print("Wrote exactly 7 configs to sub.txt successfully.")

if __name__ == "__main__":
    main()
