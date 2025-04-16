import requests
import os

# Your rotating tokens
tokens = {
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "POPCAT": "popcat",
    "TRUMP": "maga",
    "FARTCOIN": "fartcoin"
}
token_keys = list(tokens.keys())
INVEST_AMOUNT = 100

# Load index from file or default to 0
index_file = "state.txt"
if os.path.exists(index_file):
    with open(index_file, "r") as f:
        current_index = int(f.read().strip())
else:
    current_index = 0

# Get current token
token_name = token_keys[current_index]
token_id = tokens[token_name]

# Fetch prices + calculate gain
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

# Save new index for next run
next_index = (current_index + 1) % len(token_keys)
with open(index_file, "w") as f:
    f.write(str(next_index))
