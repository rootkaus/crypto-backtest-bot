import requests
import os
import datetime
import time

tokens = {
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "POPCAT": "popcat",
    "TRUMP": "maga",
    "FARTCOIN": "fartcoin"
}

INVEST_AMOUNT = 100
token_keys = list(tokens.keys())

# Use current UTC hour to determine which token to post about
current_hour = datetime.datetime.utcnow().hour
token_name = token_keys[current_hour % len(token_keys)]
token_id = tokens[token_name]

print(f"⏱️ Bot started at UTC hour: {current_hour}")
print(f"🔄 Selected token: {token_name} ({token_id})")

def fetch_prices(token_id):
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart"
    params = {"vs_currency": "usd", "days": "1"}

    for attempt in range(3):  # retry logic
        try:
            print(f"📡 Fetching price data (Attempt {attempt + 1})...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            prices = data.get("prices", [])
            if prices and len(prices) >= 2:
                return prices
            else:
                raise ValueError("Insufficient price data")
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            time.sleep(3)
    raise Exception("Failed to fetch price data after 3 attempts")

try:
    prices = fetch_prices(token_id)

    old_price = prices[0][1]
    new_price = prices[-1][1]

    amount = INVEST_AMOUNT / old_price
    value_now = amount * new_price
    change_pct = ((value_now - INVEST_AMOUNT) / INVEST_AMOUNT) * 100

    tweet = (
        f"1D Price Return — ${token_name}\n"
        f"${INVEST_AMOUNT} → ${value_now:,.2f} ({change_pct:+.2f}%)"
    )

    print(f"📤 Tweet content:\n{tweet}")

    # Send to IFTTT webhook
    webhook_url = os.getenv("IFTTT_WEBHOOK_URL")
    if not webhook_url:
        raise Exception("Missing IFTTT_WEBHOOK_URL environment variable.")

    response = requests.post(webhook_url, json={"value1": tweet}, timeout=10)

    if response.status_code != 200:
        raise Exception(f"IFTTT webhook error: {response.status_code} - {response.text}")

    print("✅ Tweet sent via IFTTT successfully!")

except Exception as e:
    print(f"❌ Bot failed: {e}")
