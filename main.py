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

def format_price_dynamic(p):
    if p >= 1:
        return f"{p:.3f}"
    s = f"{p:.12f}"
    parts = s.split('.')
    decimals = parts[1]
    # find first non-zero
    idx = next((i for i,c in enumerate(decimals) if c != '0'), len(decimals))
    return f"0.{decimals[:idx]}{decimals[idx:idx+3]}"


def get_24h_volume(token_id: str, when: datetime.date) -> float:
    """Fetch official 24h total_volume.usd from CoinGecko history endpoint."""
    date_str = when.strftime("%d-%m-%Y")
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}/history?date={date_str}"
    res = requests.get(url)
    data = res.json()
    return data.get("market_data", {}).get("total_volume", {}).get("usd", 0)


def main():
    now = datetime.datetime.utcnow()
    hour = now.hour
    token_keys = list(tokens.keys())
    token_name = token_keys[hour % len(token_keys)]
    token_id, twitter_handle = tokens[token_name]

    print(f"🕐 Bot started at: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC | Hour: {hour}")
    print(f"🪙 Selected token: ${token_name} ({token_id})")

    # Calculate dates
    today_date = now.date()
    yesterday_date = today_date - datetime.timedelta(days=1)

    try:
        # Fetch core market data
        url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
        res = requests.get(url)
        market_data = res.json().get("market_data", {})

        price = market_data.get("current_price", {}).get("usd", 0)
        price_pct = market_data.get("price_change_percentage_24h", 0)
        ath_chg = market_data.get("ath_change_percentage", {}).get("usd", 0)
        atl_chg = market_data.get("atl_change_percentage", {}).get("usd", 0)
        market_cap = market_data.get("market_cap", {}).get("usd", 0)

        # Invest ROI
        value_now = INVEST_AMOUNT * (1 + price_pct / 100)

        # Today's official 24h volume
        today_vol = get_24h_volume(token_id, today_date)
        # Yesterday's official 24h volume
        yesterday_vol = get_24h_volume(token_id, yesterday_date)

        if yesterday_vol > 0:
            vol_diff_pct = (today_vol - yesterday_vol) / yesterday_vol * 100
            vol_trend = f"[{vol_diff_pct:+.1f}%]"
        else:
            vol_trend = "[N/A]"

        # Emoji for price move
        if price_pct >= 10:
            emo = "🔥"
        elif price_pct >= 3:
            emo = "📈"
        elif price_pct <= -10:
            emo = "💀"
        elif price_pct <= -3:
            emo = "📉"
        else:
            emo = ""

        # Compose tweet
        tweet = (
            f"DEGEN DAILY — ft. ${token_name.lower()} {twitter_handle}\n\n"
            f"$100 → ${value_now:,.2f} [{price_pct:+.2f}%] {emo}\n\n"
            f"🏷️ Price: ${format_price_dynamic(price)} | Market Cap: ${market_cap/1_000_000:.1f}M\n"
            f"↕️ ATL ↑ {abs(atl_chg):.0f}% | ATH ↓ {abs(ath_chg):.0f}%\n"
            f"🔊 Volume [24h]: ${today_vol/1_000_000:.1f}M {vol_trend}\n\n"
            f"New breakdown same time tomorrow!"
        )

        print("📤 Tweet content:")
        print(tweet)

        webhook = os.getenv("IFTTT_WEBHOOK_URL")
        if webhook:
            resp = requests.post(webhook, json={"value1": tweet})
            if resp.status_code == 200:
                print("✅ Tweet sent via IFTTT successfully!")
            else:
                print(f"⚠️ IFTTT error: {resp.status_code} - {resp.text}")
    except Exception as ex:
        print(f"❌ Error: {ex}")

if __name__ == "__main__":
    main()
