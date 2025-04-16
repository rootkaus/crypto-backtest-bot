import requests
import os
import tweepy

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

try:
    # Fetch price data (1 day)
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

    # Format tweet
    tweet = (
        f"1D Price Return — ${token_name}\n"
        f"${INVEST_AMOUNT} → ${value_now:,.2f} ({change_pct:+.2f}%)"
    )
    print(tweet)

    # Authenticate with Twitter using secrets
    auth = tweepy.OAuth1UserHandler(
        os.environ["ekc2mWEAIO396uFqZgJp9KkQj"],
        os.environ["fjz1GeNizcyOsoXRZ2xxZbkrTq2W6oHrkubN5ddC3argH4oYqu"],
        os.environ["1378036200443875328-RzI81R6kguqWd19DJv1DDJanQrJtbK"],
        os.environ["HBLuToPVfsh5pyR1DK9qwyO4TN9pMmIA9U6bg4ojNK5jj"]
    )
    api = tweepy.API(auth)

    # Send tweet
    api.update_status(tweet)

except Exception as e:
    print(f"⚠️ Error with {token_name}: {e}")

# Rotate to next token
next_index = (current_index + 1) % len(token_keys)
with open(index_file, "w") as f:
    f.write(str(next_index))
