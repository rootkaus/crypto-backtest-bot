import requests
import datetime
import os

tokens = {
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "POPCAT": "popcat",
    "TRUMP": "official-trump",
    "HARAMBE": "harambe-2",
    "FARTCOIN": "fartcoin",
    "PAIN": "pain",
    "MEW": "cat-in-a-dogs-world",
    "AI16Z": "ai16z",
    "PNUT": "peanut-the-squirrel",
    "MELANIA": "melania-meme",
    "FWOG": "fwog",
    "DADDY": "daddy-tate",
    "MOODENG": "moo-deng",
    "WEN": "wen-4",
    "ZEREBRO": "zerebro",
    "JAILSTOOL": "stool-prisondente",
    "GHIBLI": "ghiblification",
    "SLERF": "slerf",
    "CABAL": "cabal",
    "DEFIANT": "defiant-2",
    "PENGU": "pudgy-penguins",
    "GIGACHAD": "gigachad-2",
    "PONKE": "ponke"
}

INVEST_AMOUNT = 100
token_keys = list(tokens.keys())

now = datetime.datetime.utcnow()
current_hour = now.hour
token_name = token_keys[current_hour % len(token_keys)]
token_id = tokens[token_name]

print(f"🕐 Bot started at: {now.strftime('%Y-%m-%d %H:%M:%S')} | Hour: {current_hour}")
print(f"🪙 Selected token: ${token_name} ({token_id})")

try:
    print("🔍 Fetching 24h price change from CoinGecko...")
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
    res = requests.get(url)
    data = res.json()

    if "market_data" not in data or "price_change_percentage_24h" not in data["market_data"]:
        raise ValueError("❌ 'market_data' or 'price_change_percentage_24h' not found in API response")

    change_pct = data["market_data"]["price_change_percentage_24h"]
    value_now = INVEST_AMOUNT * (1 + change_pct / 100)

    # Emoji logic
    if change_pct >= 10:
        emoji = "🔥"
    elif change_pct >= 3:
        emoji = "📈"
    elif change_pct <= -10:
        emoji = "💀"
    elif change_pct <= -3:
        emoji = "📉"
    else:
        emoji = ""

    tweet = (
        f"1D Price Return — ${token_name}\n"
        f"${INVEST_AMOUNT} → ${value_now:,.2f} ({change_pct:+.2f}%) {emoji}"
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
