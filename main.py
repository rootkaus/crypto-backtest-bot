import requests
import os
import datetime

# Verified 22-token list (CoinGecko ID)
tokens = {
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "POPCAT": "popcat",
    "TRUMP": "official-trump",
    "HARAMBE": "harambe",
    "FARTCOIN": "fartcoin",
    "PAIN": "pain",
    "MEW": "mew",
    "AI16Z": "ai16z",
    "PNUT": "peanut-the-squirrel",
    "MELANIA": "melania-meme",
    "FWOG": "fwog",
    "DADDY": "daddy-tate",
    "MOODENG": "mood-engines",
    "WEN": "wen-solana",
    "ZEREBRO": "zerebro",
    "JAILSTOOL": "stool-prisondente",
    "GHIBLI": "ghiblification",
    "SLERF": "slerf",
    "CABAL": "cabal",
    "DEFIANT": "defiant-2",
}

token_keys = list(tokens.keys())
INVEST_AMOUNT = 100

# UTC hour-based rotation
now = datetime.datetime.utcnow()
current_hour = now.hour
token_name = token_keys[current_hour % len(token_keys)]
token_id = tokens[token_name]

print(f"🕐 Bot started at: {now.strftime('%Y-%m-%d %H:%M:%S')} | Hour: {current_hour}")
print(f"🪙 Selected token: ${token_name} ({token_id})")

try:
    # Get 1D historical prices at hourly interval
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart?vs_currency=usd&days=1&interval=hourly"
    print("🔍 Fetching price data from CoinGecko...")
    res = requests.get(url)
    data = res.json()
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

    webhook_url = os.environ["IFTTT_WEBHOOK_URL"]
    webhook_res = requests.post(webhook_url, json={"value1": tweet})

    if webhook_res.status_code == 200:
        print("✅ Tweet sent via IFTTT successfully!")
    else:
        print(f"⚠️ IFTTT error: {webhook_res.status_code} - {webhook_res.text}")

except Exception as e:
    print(f"❌ Error: {e}")
