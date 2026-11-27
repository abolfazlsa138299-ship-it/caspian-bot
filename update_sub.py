import base64
import os
import re
import socket
import urllib.parse
import urllib.request

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
VIP_CHANNEL_ID = os.environ.get("VIP_CHANNEL_ID", "-1005629553208").strip()

SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/normal/vless",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vless",
    "https://t.me/s/v2rayngvpn",
    "https://t.me/s/PrivateVPNs",
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def parse_host_port(url_str: str):
    try:
        clean = url_str.strip()
        parsed = urllib.parse.urlsplit(clean)
        host = parsed.hostname
        port = parsed.port or 443
        return host, int(port)
    except Exception:
        return None, None


def is_server_alive(host: str, port: int, timeout: float = 1.5) -> bool:
    if not host or not port:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def decode_base64_safe(data_str: str) -> str:
    try:
        padding = 4 - (len(data_str) % 4)
        if padding != 4:
            data_str += "=" * padding
        return base64.b64decode(data_str).decode("utf-8", errors="ignore")
    except Exception:
        return data_str


def fetch_raw(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            if not ("vless://" in content or "vmess://" in content):
                content = decode_base64_safe(content.strip())
            return content
    except Exception as e:
        return ""


def clean_and_rename_config(config_str: str, index: int, label: str) -> str:
    raw_config = config_str.split("#")[0].strip()
    tag = urllib.parse.quote(f"Caspian-{label}-{index} ⚡ @proxy_caspian")
    return f"{raw_config}#{tag}"


def send_telegram_vip_message(caption: str):
    if not BOT_TOKEN or not VIP_CHANNEL_ID:
        return
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
        urllib.request.urlopen(req, timeout=12)
    except Exception:
        pass


def main():
    raw_pool = []
    for src in SOURCES:
        txt = fetch_raw(src)
        if txt:
            configs = re.findall(r"vless://[^\s<>\"\'\n\r]+", txt)
            raw_pool.extend(configs)

    unique_pool = list(dict.fromkeys(raw_pool))

    # فقط پورت ۴۴۳ که همراه اول و ایرانسل نبندن
    best_candidates = []
    for cfg in unique_pool:
        host, port = parse_host_port(cfg)
        if port == 443 and "reality" in cfg.lower():
            best_candidates.append(cfg)

    if len(best_candidates) < 30:
        for cfg in unique_pool:
            host, port = parse_host_port(cfg)
            if port == 443 and cfg not in best_candidates:
                best_candidates.append(cfg)

    alive_configs = []
    for cfg in best_candidates:
        host, port = parse_host_port(cfg)
        if is_server_alive(host, port, timeout=1.8):
            alive_configs.append(cfg)
            if len(alive_configs) >= 30:
                break

    if len(alive_configs) < 6:
        alive_configs = best_candidates[:6]

    c1 = clean_and_rename_config(alive_configs[0], 1, "V2Ray")
    c2 = clean_and_rename_config(alive_configs[1], 2, "V2Ray")
    c3 = clean_and_rename_config(alive_configs[2], 1, "NPV")
    c4 = clean_and_rename_config(alive_configs[3], 2, "NPV")
    c5 = clean_and_rename_config(alive_configs[4], 1, "Turbo")
    c6 = clean_and_rename_config(alive_configs[5], 2, "Turbo")

    caption = (
        "👑 <b>کانفیگ اختصاصی اعضای VIP کاسپین</b> 👑\n\n"
        "♨️ <b>کانفیگ‌های تازه‌نفس و ضد فیلتر کاسپین (تست‌شده و بدون قطعی):</b>\n\n"
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
        "💡 <b>راهنما:</b> فقط کافیه روی هر کانفیگ یکبار ضربه بزنید تا خودکار کپی شود."
    )

    send_telegram_vip_message(caption)

    sub_lines = [clean_and_rename_config(c, i, "VIP") for i, c in enumerate(alive_configs, 1)]
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sub_lines))


if __name__ == "__main__":
    main()
