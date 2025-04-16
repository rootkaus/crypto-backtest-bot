import requests
from replit import db

# Tokens to rotate through
tokens = {
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "POPCAT": "popcat",
    "TRUMP": "maga",
    "FARTCOIN": "fartcoin"
}
token_keys = list(tokens.keys())

# Get current index from DB, default to 0
current_index = db.get("current_index") or 0
token_name = token_keys[current_index]
token_id = tokens[token_name]

INVEST_AMOUNT = 100

try:
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart?vs_currency=usd&days=7"
    data = requests.get(url).json()
    prices = data["prices"]

    if not prices or len(prices) < 2:
        raise Exception("Not enough data")

    old_price = prices[0][1]
    new_price = prices[-1][1]

    amount = INVEST_AMOUNT / old_price
    value_now = amount * new_price
    change_pct = ((value_now - INVEST_AMOUNT) / INVEST_AMOUNT) * 100

    print(f"🪙 If you spent ${INVEST_AMOUNT} on ${token_name} 7 days ago, you’d have ${value_now:,.2f} today ({change_pct:+.2f}%)")
    print("-" * 60)

except Exception as e:
    print(f"⚠️ Error with {token_name}: {e}")

# Update index for next run
db["current_index"] = (current_index + 1) % len(token_keys)
