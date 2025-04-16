import os
import requests
import json

tokens = {
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "POPCAT": "popcat",
    "TRUMP": "maga",
    "FARTCOIN": "fartcoin"
}
token_keys = list(tokens.keys())
INVEST_AMOUNT = 100

# Load token index from state file
index_file = "state.txt"
if os.path.exists(index_file):
    with open(index_file, "r") as f:
        current_index = int(f.read().strip())
else:
    current_index = 0

token_name = token_keys[current_index]
token_id = tokens[token_name]

try:
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

    tweet_text = (
        f"1D Price Return — ${token_name}\n"
        f"${INVEST_AMOUNT} → ${value_now:,.2f} ({change_pct:+.2f}%)"
    )
    print(tweet_text)

    # Twitter v2 API with Bearer Token
    bearer_token = os.environ["TWITTER_BEARER_TOKEN"]

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": tweet_text
    }

    response = requests.post(
        "https://api.twitter.com/2/tweets",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code != 201:
        raise Exception(f"Twitter API error {response.status_code}: {response.text}")
    else:
        print("✅ Tweet sent!")

except Exception as e:
    print(f"⚠️ Error with {token_name}: {e}")

# Save the next token index
next_index = (current_index + 1) % len(token_keys)
with open(index_file, "w") as f:
    f.write(str(next_index))
