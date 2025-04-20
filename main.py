import requests
import datetime
import os

# Updated tokens with CoinGecko IDs and Twitter handles
tokens = {
    "WIF": ("dogwifcoin", "@dogwifcoin"),
    "BONK": ("bonk", "@bonk_inu"),
    "POPCAT": ("popcat", "@POPCATSOLANA"),
    "TRUMP": ("official-trump", "@GetTrumpMemes"),
    "TITCOIN": ("titcoin-2", "@TheTitCoin"),
    "FARTCOIN": ("fartcoin", "@FartCoinOfSOL"),
    "PAIN": ("pain", "@pain"),
    "MEW": ("cat-in-a-dogs-world", "@mew"),
    "AI16Z": ("ai16z", "@elizaos"),
    "PNUT": ("peanut-the-squirrel", "@pnutsolana"),
    "RFC": ("retard-finder-coin", "@RFindercoin"),
    "FWOG": ("fwog", "@itsafwog"),
    "JAILSTOOL": ("stool-prisondente", "@stoolpresidente"),
    "MOODENG": ("moo-deng", "@MooDengSOL"),
    "WEN": ("wen-4", "@wenwencoin"),
    "ZEREBRO": ("zerebro", "@0xzerebro"),
    "GHIBLI": ("ghiblification", "@ghibli"),
    "SLERF": ("slerf", "@Slerfsol"),
    "DARK": ("dark-eclipse", "@darkresearchai"),
    "DEFIANT": ("defiant-2", "@DefiantOnSol"),
    "PENGU": ("pudgy-penguins", "@pudgypenguins"),
    "GIGACHAD": ("gigachad-2", "@GIGACHAD_meme"),
    "PONKE": ("ponke", "@ponkesol"),
}

INVEST_AMOUNT = 100
token_keys = list(tokens.keys())

now = datetime.datetime.utcnow()
current_hour = now.hour
token_name = token_keys[current_hour % len(token_keys)]
token_id, twitter_handle = tokens[token_name]

print(f"🕐 Bot started at: {now.strftime('%Y-%m-%d %H:%M:%S')} | Hour: {current_hour}")
print(f"🪙 Selected token: ${token_name} ({token_id})")

def format_price_dynamic(p):
    if p >= 1:
        return f"{p:.3f}"
    else:
        s = f"{p:.12f}"
        parts = s.split(".")
        decimals = parts[1]
        non_zero = next((i for i, c in enumerate(decimals) if c != "0"), len(decimals))
        return f"0.{decimals[:non_zero]}{decimals[non_zero:non_zero+3]}"

try:
    # 1. Fetch on‐chain market data
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
    res = requests.get(url)
    data = res.json()["market_data"]

    price = data["current_price"]["usd"]
    price_pct = data["price_change_percentage_24h"]
    ath_drop = data["ath_change_percentage"]["usd"]
    atl_rise = data["atl_change_percentage"]["usd"]
    market_cap = data["market_cap"]["usd"]
    volume_24h = data["total_volume"]["usd"]

    value_now = INVEST_AMOUNT * (1 + price_pct/100)

    # 2. Get 2‑day chart for 24h vs prior‑24h volume
    chart_url = (
        f"https://api.coingecko.com/api/v3/coins/{token_id}"
        f"/market_chart?vs_currency=usd&days=2"
    )
    vol_chart = requests.get(chart_url).json().get("total_volumes", [])

    if vol_chart:
        # timestamp in ms of latest sample
        now_ts, now_vol = vol_chart[-1]
        target_ts = now_ts - 24*60*60*1000  # 24h ago

        # find the sample closest to 24 h ago
        past_ts, past_vol = min(vol_chart, key=lambda x: abs(x[0] - target_ts))

        if past_vol:
            vol_diff_pct = (now_vol - past_vol) / past_vol * 100
            vol_trend = f"[{vol_diff_pct:+.1f}%]"
        else:
            vol_trend = "[N/A]"
    else:
        now_vol = volume_24h
        vol_trend = ""

    # 3. Price emoji
    if price_pct >= 10:
        emoji = "🔥"
    elif price_pct >= 3:
        emoji = "📈"
    elif price_pct <= -10:
        emoji = "💀"
    elif price_pct <= -3:
        emoji = "📉"
    else:
        emoji = ""

    # 4. Compose tweet
    tweet = (
        f"DEGEN DAILY — ft. ${token_name.lower()} {twitter_handle}\n\n"
        f"$100 → ${value_now:,.2f} [{price_pct:+.2f}%] {emoji}\n\n"
        f"🏷️ Price: ${format_price_dynamic(price)} | Market Cap: ${market_cap/1_000_000:.1f}M\n"
        f"↕️ ATL ↑ {abs(atl_rise):.0f}% | ATH ↓ {abs(ath_drop):.0f}%\n"
        f"🔊 Volume [24h]: ${now_vol/1_000_000:.1f}M {vol_trend}\n\n"
        "New breakdown same time tomorrow!"
    )

    print("📤 Tweet content:")
    print(tweet)

    # 5. Send via IFTTT
    webhook_url = os.environ["IFTTT_WEBHOOK_URL"]
    resp = requests.post(webhook_url, json={"value1": tweet})
    if resp.status_code == 200:
        print("✅ Tweet sent via IFTTT successfully!")
    else:
        print(f"⚠️ IFTTT error: {resp.status_code} — {resp.text}")

except Exception as e:
    print(f"❌ Error: {e}")
