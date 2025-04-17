import requests
import os
import datetime

tokens = {
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "POPCAT": "popcat",
    "TRUMP": "maga",
    "FARTCOIN": "fartcoin"
}

token_keys = list(tokens.keys())
INVEST_AMOUNT = 100

# Get full UTC time and extract current hour
now = datetime.datetime.utcnow()
current_hour = now.hour
print(f"⏰ Bot started at UTC time: {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC hour: {current_hour})")

# Determine which token to post
token_name = token_keys[current_hour % len(token_keys)]
token_id = tokens[token_name]
print(f"🐶 Selected token: {token_name} ({token_id})")

try:
    print("🧪 Fetching price data...")
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart?vs_currency=usd&days=1"
    data = requests.get(url).json()
    prices = data.get("prices", [])

    if not prices or len(prices) < 2:
        raise Exception("Not enough price data.")

    old_price = prices[0][1]
    new_price = prices[-1][1]

    amount = INVEST_AMOUNT / old_price
    value_now = amount * new_price
    change_pct = ((value_now - INVEST_AMOUNT) / INVEST_AMOUNT) * 100

    tweet = (
        f"1D Price Return — ${token_name}\n"
        f"${INVEST_AMOUNT} → ${value_now:,.2f} ({change_pct:+.2f}%)"
    )

    print("📤 Tweet content:")
    print(tweet)

    # Trigger IFTTT webhook
    webhook_url = os.environ["IFTTT_WEBHOOK_URL"]
    response = requests.post(webhook_url, json={"value1": tweet})

    if response.status_code == 200:
        print("✅ Tweet sent via IFTTT successfully!")
    else:
        print(f"⚠️ IFTTT response error: {response.status_code} - {response.text}")

except Exception as e:
    print(f"❌ Error while processing {token_name}: {e}")
