import requests
import os
import datetime

# Token list (name -> address)
tokens = {
    "WIF": "Es9vMFrzasXbU9CNRVvn9qxUt6G3Aay6He6MoY7V9N6i",
    "BONK": "DezX1K7RY1LT9TT3pS9enF7kNB2nXpsQ8cY3dPAgEv7t",
    "POPCAT": "8cxtTZijAX38Az8GUG9m3z8j3U6q4CZy3EJWFiD8jGmh",
    "TRUMP": "9rA2GHTRaQ5zWdPV3LhK6UM27yXxCe8vW8z8tb6gzQvi",
    "FARTCOIN": "9ZmpivZzPgbYm8JbEt3xjXciWok1Yj2vnk7r8FBHb5fU",
    "PAIN": "GVxLJHP5v57AFQ6QEjG7RT1U9kJMYN24EBeEUxBd5KeD",
    "MEW": "2xsPmn8bRZzNPRFY62qT7nPfrVP2RD5n3J9SRT8WQuFq",
    "AI16Z": "HeLp6NuQkmYB4pYWo2zYs22mESHXPQYzXbB8n4V98jwC",
    "PNUT": "C6jdLE1N5Ub8EfX9xnGHiQWdGZ6UV9axLfS6gEbPbgpp",
    "MELANIA": "G8kHJEMQLnyrurUXu3uZREAS6VXZmgX4q3qxvbgPf8Hd",
    "FWOG": "FwogFwogFwogFwogFwogFwogFwogFwogFwogFwog",
    "DADDY": "9y64Uk9tZwF2oyyXjdtDzKnA6nnP6u44QjEcz3bUzNbe",
    "MOODENG": "7s5CvGEER36jBJoLzyHgkiZtwBAJcZibzBnsvcdTb2cT",
    "WEN": "wenxWENxWENxWENxWENxWENxWENxWENxWENxWENxWENx",
    "ZEREBRO": "8x5VqbHA8D7NkD52uNuS5nnt3PwA8pLD34ymskeSo2Wn",
    "JAILSTOOL": "AxriehR6Xw3adzHopnvMn7GcpRFcD41ddpiTWMg6pump",
    "GHIBLI": "4TBi66vi32S7J8X1A6eWfaLHYmUXu7CStcEmsJQdpump",
    "SLERF": "7BgBvyjrZX1YKz4oh9mjb8ZScatkkwb8DzFx7LoiVkM3",
    "ITALIANROT": "BQX1cjcRHXmrqNtoFWwmE5bZj7RPneTmqXB979b2pump",
    "KAPIBALA": "9WyRszmxLf1e9nWAVf4p7j7S2ektkLu74PTLVVKLpump",
    "CABAL": "6imW6S8jjGQTug1BaBMXU6azkcJsCCFnVGArzeHGpump",
    "DEFIANT": "DPTP4fUfWuwVTgCmttWBu6Sy5B9TeCTBjc2YKgpDpump"
}

token_keys = list(tokens.keys())
INVEST_AMOUNT = 100

# Use UTC minute to rotate fast (for testing)
now = datetime.datetime.utcnow()
current_minute = now.minute
token_name = token_keys[current_minute % len(token_keys)]
token_id = tokens[token_name]

print(f"⏰ Bot started at UTC time: {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC minute: {current_minute})")
print(f"🪙 Token: ${token_name} ({token_id})")

try:
    print("🧪 Fetching price history from Birdeye...")

    from_timestamp = int((now - datetime.timedelta(days=1)).timestamp())
    url = f"https://public-api.birdeye.so/public/price/history?address={token_id}&from={from_timestamp}&interval=1h"

    headers = {
        "X-API-KEY": os.environ["BIRDEYE_API_KEY"]
    }

    response = requests.get(url, headers=headers)
    print("📦 Raw API response:")
    print(response.text)

    data = response.json()
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
    res = requests.post(webhook_url, json={"value1": tweet})

    if res.status_code == 200:
        print("✅ Tweet sent via IFTTT successfully!")
    else:
        print(f"⚠️ IFTTT response error: {res.status_code} - {res.text}")

except Exception as e:
    print(f"❌ Error: {e}")
