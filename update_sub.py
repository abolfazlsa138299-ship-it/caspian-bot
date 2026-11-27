import os
import json
import urllib.request
import re
import urllib.parse
import base64
import html

BOT_TOKEN = "9268228114:AAFpg07l6AjXfu5TtdNirukEUZZiLzCBC2Y"
VIP_CHANNEL_ID = -1005629553208

# معتبرترین سورس‌های کانفیگ VLESS Reality مخصوص ایران
SOURCES = [
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/reality",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/reality"
]

def fetch_reality_configs():
    found = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in SOURCES:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                text = resp.read().decode("utf-8", errors="ignore")
                for line in text.splitlines():
                    line = line.strip()
                    if line.startswith("vless://") and ("reality" in line.lower() or "security=reality" in line.lower() or "443" in line):
                        if line not in found:
                            found.append(line)
        except Exception as e:
            print(f"Error reading {url}: {e}")
        if len(found) >= 20:
            break
    return found

def send_vip_post(configs):
    v2_1 = html.escape(configs[0].split("#")[0] + "#⚡️ Caspian | V2Ray 1")
    v2_2 = html.escape(configs[1].split("#")[0] + "#⚡️ Caspian | V2Ray 2")

    npv_1 = html.escape(configs[2].split("#")[0] + "#⚡️ Caspian | NPV Tunnel 1")
    npv_2 = html.escape(configs[3].split("#")[0] + "#⚡️ Caspian | NPV Tunnel 2")

    dual_1 = html.escape(configs[4].split("#")[0] + "#⚡️ Caspian | دوکاره 1")
    dual_2 = html.escape(configs[5].split("#")[0] + "#⚡️ Caspian | دوکاره 2")

    caption = (
        "👑 <b>پست اختصاصی اعضای کاسپین VIP</b> 👑\n\n"
        "کانفیگ‌های پرسرعت و تست‌شده اختصاصی (VLESS Reality):\n\n"
        "🔹 <b>کانفیگ‌های مخصوص V2Ray:</b>\n"
        f"1️⃣ <code>{v2_1}</code>\n\n"
        f"2️⃣ <code>{v2_2}</code>\n\n"
        "🔹 <b>کانفیگ‌های مخصوص NPV Tunnel:</b>\n"
        f"1️⃣ <code>{npv_1}</code>\n\n"
        f"2️⃣ <code>{npv_2}</code>\n\n"
        "🔹 <b>کانفیگ‌های دوکاره (پرسرعت):</b>\n"
        f"1️⃣ <code>{dual_1}</code>\n\n"
        f"2️⃣ <code>{dual_2}</code>\n\n"
        "📶 <b>مناسب برای:</b> همراه اول، ایرانسل، رایتل و وای‌فای 📊\n"
        "💡 <b>راهنما:</b> فقط کافیه روی هر کانفیگ یکبار ضربه بزنید تا خودکار کپی بشه\n"
        "و داخل برنامه اضافه کنید."
    )

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": VIP_CHANNEL_ID,
        "text": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, headers={"Content-Type": "application/json"})
    
    with urllib.request.urlopen(req, timeout=12) as response:
        print("پیام با موفقیت به تلگرام ارسال شد!")

def main():
    configs = fetch_reality_configs()
    if not configs:
        print("کانفیگی پیدا نشد.")
        return

    # ذخیره در فایل ساب‌اسکریپشن
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(configs[:15]))
    print("فایل sub.txt به‌روزرسانی شد.")

    # ارسال ۶ کانفیگ به کانال VIP
    vip_selected = configs[:6] if len(configs) >= 6 else (configs * 6)[:6]
    send_vip_post(vip_selected)

if __name__ == "__main__":
    main()
