import requests
import os
import datetime

# 24 verified token addresses (your list)
tokens = {
    "WIF": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
    "TRUMP": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
    "HARAMBE": "GbCAE65q8yNubtJD3cxRi6tGBa94cVx1MEu99sR4mpEh",
    "FARTCOIN": "9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump",
    "PAIN": "1Qf8gESP4i6CFNWerUSDdLKJ9U1LpqTYvjJ2MM4pain",
    "MEW": "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5",
    "AI16Z": "HeLp6NuQkmYB4pYWo2zYs22mESHXPQYzXbB8n4V98jwC",
    "PNUT": "2qEHjDLDLbuBgRYvsxhc5D6uDWAivNFZGan56P1tpump",
    "MELANIA": "FUAfBo2jgks6gB4Z4LfZkqSZgzNucisEHqnNebaRxM1P",
    "FWOG": "A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump",
    "DADDY": "4Cnk9EPnW5ixfLZatCPJjDB1PUtcRpVVgTQukm9epump",
    "MOODENG": "ED5nyyWEzpPPiWimP8vYm7sD7TD3LAt3Q3gRTWHzPJBY",
    "WEN": "WENWENvqqNya429ubCdR81ZmD69brwQaaBYY6p3LCpk",
    "ZEREBRO": "8x5VqbHA8D7NkD52uNuS5nnt3PwA8pLD34ymskeSo2Wn",
    "JAILSTOOL": "AxriehR6Xw3adzHopnvMn7GcpRFcD41ddpiTWMg6pump",
    "GHIBLI": "4TBi66vi32S7J8X1A6eWfaLHYmUXu7CStcEmsJQdpump",
    "SLERF": "7BgBvyjrZX1YKz4oh9mjb8ZScatkkwb8DzFx7LoiVkM3",
    "ITALIANROT": "BQX1cjcRHXmrqNtoFWwmE5bZj7RPneTmqXB979b2pump",
    "KAPIBALA": "9WyRszmxLf1e9nWAVf4p7j7S2ektkLu74PTLVVKLpump",
    "CABAL": "6imW6S8jjGQTug1BaBMXU6azkcJsCCFnVGArzeHGpump",
    "DEFIANT": "DPTP4fUfWuwVTgCmttWBu6Sy5B9TeCTBjc2YKgpDpump",
}

INVEST_AMOUNT = 100
token_keys = list(tokens.keys())

# Rotate using current UTC hour
now = datetime.datetime.utcnow()
current_hour = now.hour
token_name = token_keys[current_hour % len(token_keys)]
token_address = tokens[token_name]

print(f"⏰ Bot started at: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
print(f"📦 Token: ${token_name} ({token_address})")

try:
    print("📡 Fetching price history from Birdeye...")
    url = f"https://public-api.birdeye.so/public/pricehistory"
    params = {
        "address": token_address,
        "address_type": "token",
        "interval": "1d",
        "from": int((now - datetime.timedelta(days=1)).timestamp()),
        "to": int(now.timestamp()),
    }
    headers = {
        "x-chain": "solana",
        "x-api-key": os.environ["BIRDEYE_API_KEY"]
    }

    res = requests.get(url, headers=headers, params=params)
    data = res.json().get("data", [])

    if not data or len(data) < 2:
        raise Exception("Not enough price data.")

    old_price = data[0]["value"]
    new_price = data[-1]["value"]

    amount = INVEST_AMOUNT / old_price
    value_now = amount * new_price
    change_pct = ((value_now - INVEST_AMOUNT) / INVEST_AMOUNT) * 100

    tweet = (
        f"1D Price Return — ${token_name}\n"
        f"${INVEST_AMOUNT} → ${value_now:,.2f} ({change_pct:+.2f}%)"
    )

    print("📝 Composed tweet:")
    print(tweet)

    # Send to IFTTT webhook
    webhook_url = os.environ["IFTTT_WEBHOOK_URL"]
    response = requests.post(webhook_url, json={"value1": tweet})

    if response.status_code == 200:
        print("✅ Tweet sent via IFTTT!")
    else:
        print(f"⚠️ IFTTT error: {response.status_code} - {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")
