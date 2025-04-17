import requests
import datetime

# Verified CoinGecko token list (name -> CoinGecko ID)
tokens = {
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "POPCAT": "popcat",
    "TRUMP": "official-trump",
    "HARAMBE": "harambe-on-solana",
    "FARTCOIN": "fartcoin",
    "PAIN": "pain-coin",
    "MEW": "mew",
    "AI16Z": "ai16z",
    "PNUT": "peanut-the-squirrel",
    "MELANIA": "melania-meme",
    "FWOG": "fwog-coin",
    "DADDY": "daddy-tate",
    "MOODENG": "moodeng",
    "WEN": "wen-solana",
    "ZEREBRO": "zerebro",
    "JAILSTOOL": "jailstool",
    "GHIBLI": "ghiblification",
    "SLERF": "slerf",
    "ITALIANROT": "italianrot",
    "CABAL": "cabal",
    "DEFIANT": "defiant-2"
}

token_keys = list(tokens.keys())
INVEST_AMOUNT = 100

now = datetime.datetime.utcnow()
current_hour = now.hour
token_name = token_keys[current_hour % len(token_keys)]
coingecko_id = tokens[token_name]

print(f"⏰ Bot started at: {now.strftime('%Y-%m-%d %H:%M:%S')} | Hour: {current_hour}")
print(f"🪙 Selected token: ${token_name} ({coingecko_id})")

try:
    print("🔍 Fetching price data from CoinGecko...")

    url = (
        f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart"
        f"?vs_currency=usd&days=1&interval=hourly"
    )

    response = requests.get(url)
    data = response.json()

    if "prices" not in data or len(data["prices"]) < 2:
        raise Exception("Not enough price data.")

    old_price = data["prices"][0][1]
    new_price = data["prices"][-1][1]

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
    res = requests.post(webhook_url, json={"value1": tweet})

    if res.status_code == 200:
        print("✅ Tweet sent via IFTTT successfully!")
    else:
        print(f"⚠️ IFTTT error: {res.status_code} - {res.text}")

except Exception as e:
    print(f"❌ Error: {e}")
