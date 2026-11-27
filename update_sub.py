import urllib.request
import re
import socket
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# سورس‌های معتبر کانفیگ‌های فعال
SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/base64/mix",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt"
]

def fetch_configs():
    raw_configs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for src in SOURCES:
        try:
            req = urllib.request.Request(src, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                # اگر بیس۶۴ بود دیکود کن، اگر نبود مستقیم بخون
                lines = content.splitlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith(("vless://", "vmess://", "trojan://", "ss://")):
                        raw_configs.append(line)
        except Exception as e:
            print(f"Error fetching {src}: {e}")
    return list(set(raw_configs))

def check_config_alive(config):
    try:
        parsed = urllib.parse.urlparse(config)
        host = parsed.hostname
        port = parsed.port
        if not host or not port:
            return None

        # تست اتصال سریع به سرور
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.2)
        res = sock.connect_ex((host, int(port)))
        sock.close()

        if res == 0:
            return config
    except:
        pass
    return None

def main():
    print("در حال دریافت کانفیگ‌های V2Ray و NPV...")
    all_configs = fetch_configs()
    print(f"تعداد {len(all_configs)} کانفیگ پیدا شد. در حال فیلتر بهترین‌ها...")

    alive_configs = []
    with ThreadPoolExecutor(max_workers=25) as executor:
        results = executor.map(check_config_alive, all_configs[:120])
        for r in results:
            if r:
                alive_configs.append(r)
                if len(alive_configs) >= 15: # ۱۵ تا از بهترین‌ها
                    break

    # برچسب‌گذاری برای V2Ray و NPV
    final_labeled = []
    for i, cfg in enumerate(alive_configs):
        base_url = cfg.split("#")[0]
        if i % 3 == 0:
            tag = f"⚡️ Caspian | مخصوص V2Ray #{i+1}"
        elif i % 3 == 1:
            tag = f"⚡️ Caspian | مخصوص NPV Tunnel #{i+1}"
        else:
            tag = f"⚡️ Caspian | دوکاره (V2Ray + NPV) #{i+1}"
        
        final_labeled.append(f"{base_url}#{urllib.parse.quote(tag)}")

    if final_labeled:
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_labeled))
        print("فایل sub.txt با موفقیت با بهترین کانفیگ‌های V2Ray و NPV آپدیت شد.")
    else:
        print("کانفیگ جدیدی پیدا نشد.")

if __name__ == "__main__":
    main()
