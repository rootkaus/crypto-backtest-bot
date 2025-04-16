import os
import requests
import tweepy

# --- Settings ---
tokens = {
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "POPCAT": "popcat",
    "TRUMP": "maga",
    "FARTCOIN": "fartcoin"
}
INVEST_AMOUNT = 100
index_file = "state.txt"

# --- Load which token to run ---
token_keys = list(tokens.keys())
if os.path.exists(index_file):
    with open(index_file, "r") as f:
        current_index = int(f.read().strip())
else:
    current_index = 0

token_name = token_keys[current_index]
token_id = tokens[token_name]

try:
    # --- Fetch price data from CoinGecko ---
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart?vs_currency=usd&days=1"
    data = requests.get(url).json()
    prices = data["prices"]

    if not prices or len(prices) < 2:
        raise Exception("Not enough data points")

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

    # --- Twitter: Authenticate and post ---
    auth = tweepy.OAuth1UserHandler(
        os.environ["TWITTER_API_KEY"],
        os.environ["TWITTER_API_SECRET"],
        os.environ["TWITTER_ACCESS_TOKEN"],
        os.environ["TWITTER_ACCESS_SECRET"]
    )
    api = tweepy.API(auth)
    api.update_status(tweet)

except Exception as e:
    print(f"⚠️ Error with {token_name}: {e}")

# --- Save next token index ---
next_index = (current_index + 1) % len(token_keys)
with open(index_file, "w") as f:
    f.write(str(next_index))
