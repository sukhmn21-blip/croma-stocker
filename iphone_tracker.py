import time
import os
import requests

# --- CONFIGURATION FROM RAILWAY ENVIRONMENT VARIABLES ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))

TRACKED_ITEMS = [
    {
        "color": "Black",
        "url": "https://www.apple.com/shop/buy-iphone/iphone-17/6.3%22-display-256gb-black"
    },
    {
        "color": "White",
        "url": "https://www.apple.com/shop/buy-iphone/iphone-17/6.3%22-display-256gb-white"
    },
    {
        "color": "Mist Blue",
        "url": "https://www.apple.com/shop/buy-iphone/iphone-17/6.3%22-display-256gb-mist-blue"
    },
    {
        "color": "Lavender",
        "url": "https://www.apple.com/shop/buy-iphone/iphone-17/6.3%22-display-256gb-lavender"
    },
    {
        "color": "Sage",
        "url": "https://www.apple.com/shop/buy-iphone/iphone-17/6.3%22-display-256gb-sage"
    }
]

notified_status = {item["color"]: False for item in TRACKED_ITEMS}

def send_telegram_alert(message):
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(tg_url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Failed to send Telegram alert: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")

def check_stock():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking Apple Store inventory...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    for item in TRACKED_ITEMS:
        color = item["color"]
        page_url = item["url"]
        
        try:
            response = requests.get(page_url, headers=headers, timeout=15)
            if response.status_code == 200:
                page_text = response.text.lower()
                is_available = "add to bag" in page_text and "currently unavailable" not in page_text
                
                if is_available:
                    if not notified_status[color]:
                        msg = f"🚨 *IPHONE 17 STOCK ALERT!* 🚨\n\nColor: *{color} (256GB)* is available!\n\n🔗 [Buy Now]({page_url})"
                        send_telegram_alert(msg)
                        notified_status[color] = True
                        print(f"[IN STOCK] Alert sent for {color}!")
                else:
                    notified_status[color][:] = False if isinstance(notified_status[color], list) else False
                    notified_status[color] = False
                    print(f"[-] {color} 256GB is out of stock.")
            else:
                print(f"[ERROR] Could not reach Apple store for {color} (Status: {response.status_code})")
        except Exception as e:
            print(f"[EXCEPTION] Error checking {color}: {e}")

if __name__ == "__main__":
    print("=== Starting iPhone 17 Stock Tracker Bot ===")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[CRITICAL] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables are missing!")
    while True:
        check_stock()
        time.sleep(CHECK_INTERVAL_SECONDS)
