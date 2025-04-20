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
print(f"🌐 Selected token: ${token_name.upper()} ({token_id})")

def format_price_dynamic(p):
    if p >= 1:
        return f"{p:.3f}"
    else:
        s = f"{p:.12f}"
        parts = s.split(".")
        decimals = parts[1]
        non_zero_index = next((i for i, c in enumerate(decimals) if c != "0"), len(decimals))
        digits_to_show = decimals[non_zero_index:non_zero_index + 3]
        return f"0.{decimals[:non_zero_index]}{digits_to_show}"

try:
    # Fetch main token data
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
    res = requests.get(url)
    data = res.json()
    market_data = data["market_data"]

    price = market_data["current_price"]["usd"]
    price_pct = market_data["price_change_percentage_24h"]
    ath_change = market_data["ath_change_percentage"]["usd"]
    atl_change = market_data["atl_change_percentage"]["usd"]
    market_cap = market_data["market_cap"]["usd"]
    value_now = INVEST_AMOUNT * (1 + price_pct / 100)

    # Volume analysis using 48h data
    volume_url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart?vs_currency=usd&days=2"
    volume_res = requests.get(volume_url)
    vol_data = volume_res.json().get("total_volumes", [])

    if len(vol_data) >= 49:  # 24h + 24h + 1
        v0 = vol_data[0][1]
        v24 = vol_data[24][1]
        v48 = vol_data[48][1]

        day1 = v24 - v0
        day2 = v48 - v24

        print(f"📊 Volume Debug → Day 1: ${day1:,.2f}, Day 2: ${day2:,.2f}")

        volume_24h = day2
        try:
            vol_pct_change = ((day2 - day1) / day1) * 100
            volume_trend = f"[{vol_pct_change:+.1f}%]"
        except ZeroDivisionError:
            volume_trend = ""
    else:
        print("⚠️ Not enough volume data points (need 49)")
        volume_24h = market_data["total_volume"]["usd"]
        volume_trend = ""

    # Emoji based on price %
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

    # Format Tweet
    tweet = (
        f"DEGEN DAILY — ft. ${token_name.lower()} {twitter_handle}\n\n"
        f"$100 → ${value_now:,.2f} [{price_pct:+.2f}%] {emoji}\n\n"
        f"🏷️ Price: ${format_price_dynamic(price)} | Market Cap: ${market_cap/1_000_000:.1f}M\n"
        f"↕️ ATL ↑ {abs(atl_change):,.0f}% | ATH ↓ {abs(ath_change):.0f}%\n"
        f"🔊 Volume [24h]: ${volume_24h/1_000_000:.1f}M {volume_trend}\n\n"
        f"New breakdown same time tomorrow!"
    )

    print("📤 Tweet content:")
    print(tweet)

    webhook_url = os.environ["IFTTT_WEBHOOK_URL"]
    webhook_res = requests.post(webhook_url, json={"value1": tweet})

    if webhook_res.status_code == 200:
        print("✅ Tweet sent via IFTTT successfully!")
    else:
        print(f"⚠️ IFTTT error: {webhook_res.status_code} - {webhook_res.text}")

except Exception as e:
    print(f"❌ Error: {e}")
