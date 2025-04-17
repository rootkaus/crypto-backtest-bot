import requests
import os
import datetime

# Confirmed working tokens (name -> address)
tokens = {
    "WIF": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
    "TRUMP": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN"
}

INVEST_AMOUNT = 100
token_keys = list(tokens.keys())

# UTC hour to rotate
now = datetime.datetime.utcnow()
current_hour = now.hour
token_name = token_keys[current_hour % len(token_keys)]
token_id = tokens[token_name]

print(f"🕐 Bot started at: {now.strftime('%Y-%m-%d %H:%M:%S')} | Hour: {current_hour}")
print(f"🪙 Selected token: ${token_name} ({token_id})")

try:
    from_timestamp = int((now - datetime.timedelta(days=1)).timestamp())
    url = f"https://public-api.birdeye.so/public/price/history?address={token_id}&from={from_timestamp}&interval=1h"
    headers = { "X-API-KEY": os.environ["BIRDEYE_API_KEY"] }

    print("🔍 Fetching price data...")
    res = requests.get(url, headers=headers)
    data = res.json()

    print("📦 Raw response keys:", data.keys())

    prices = data.get("data", {}).get("items", [])
    if not prices or len(prices) < 2:
        raise Exception("Not enough price data.")

    old_price = prices[0]["value"]
    new_price = prices[-1]["value"]

    amount = INVEST_AMOUNT / old_price
    value_now = amount * new_price
    change_pct = ((value_now - INVEST_AMOUNT) / INVEST_AMOUNT) * 100

    tweet = (
        f"1D Price Return — ${token_name}\n"
        f"${INVEST_AMOUNT} → ${value_now:,.2f} ({change_pct:+.2f}%)"
    )

    print("📤 Tweet content:")
    print(tweet)

    webhook_url = os.environ["IFTTT_WEBHOOK_URL"]
    webhook_res = requests.post(webhook_url, json={"value1": tweet})

    if webhook_res.status_code == 200:
        print("✅ Tweet sent via IFTTT successfully!")
    else:
        print(f"⚠️ IFTTT error: {webhook_res.status_code} - {webhook_res.text}")

except Exception as e:
    print(f"❌ Error: {e}")
