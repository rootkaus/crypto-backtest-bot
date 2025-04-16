import requests
import os

# Tokens to rotate
tokens = {
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "POPCAT": "popcat",
    "TRUMP": "maga",
    "FARTCOIN": "fartcoin"
}
token_keys = list(tokens.keys())
INVEST_AMOUNT = 100

# Load index from file
index_file = "state.txt"
if os.path.exists(index_file):
    with open(index_file, "r") as f:
        current_index = int(f.read().strip())
else:
    current_index = 0

# Get current token info
token_name = token_keys[current_index]
token_id = tokens[token_name]

try:
    # Fetch 1-day historical prices
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart?vs_currency=usd&days=1"
    data = requests.get(url).json()
    prices = data["prices"]

    if not prices or len(prices) < 2:
        raise Exception("Not enough data")

    old_price = prices[0][1]
    new_price = prices[-1][1]

    amount = INVEST_AMOUNT / old_price
    value_now = amount * new_price
    change_pct = ((value_now - INVEST_AMOUNT) / INVEST_AMOUNT) * 100

    tweet = (
        f"1D Price Return — ${token_name}\n"
        f"${INVEST_AMOUNT} → ${value_now:,.2f} ({change_pct:+.2f}%)"
    )
    print(tweet)

    # Send tweet via v2 API using Bearer Token
    headers = {
        "Authorization": f"Bearer {os.environ['TWITTER_BEARER_TOKEN']}",
        "Content-Type": "application/json"
    }
    payload = {"text": tweet}
    response = requests.post("https://api.twitter.com/2/tweets", json=payload, headers=headers)

    if response.status_code != 201:
        raise Exception(f"Twitter API error: {response.status_code} {response.text}")

except Exception as e:
    print(f"⚠️ Error with {token_name}: {e}")

# Rotate to next token
next_index = (current_index + 1) % len(token_keys)
with open(index_file, "w") as f:
    f.write(str(next_index))
