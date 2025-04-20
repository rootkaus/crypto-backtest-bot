import requests
import datetime
import os

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
now = datetime.datetime.utcnow()
token_keys = list(tokens.keys())
token_name = token_keys[now.hour % len(token_keys)]
token_id, twitter_handle = tokens[token_name]

print(f"🕐 Bot started at: {now.strftime('%Y-%m-%d %H:%M:%S UTC')} | Hour: {now.hour}")
print(f"🪙 Selected token: ${token_name} ({token_id})")

def format_price_dynamic(p):
    if p >= 1:
        return f"{p:.3f}"
    s = f"{p:.12f}"
    dec = s.split(".")[1]
    nz = next((i for i,c in enumerate(dec) if c!="0"), len(dec))
    digits = dec[nz:nz+3]
    return f"0.{dec[:nz]}{digits}"

def get_yesterday_volume(token_id, dt):
    # dt is a datetime for "today"; we want yesterday's date in dd-mm-YYYY
    yday = (dt - datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    hist = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{token_id}/history?date={yday}"
    ).json()
    return hist.get("market_data", {}).get("total_volume", {}).get("usd")

try:
    # 1) fetch main market_data
    r = requests.get(f"https://api.coingecko.com/api/v3/coins/{token_id}")
    m = r.json()["market_data"]

    price       = m["current_price"]["usd"]
    price_pct   = m["price_change_percentage_24h"]
    ath_chg     = m["ath_change_percentage"]["usd"]
    atl_chg     = m["atl_change_percentage"]["usd"]
    vol_today   = m["total_volume"]["usd"]
    mcap        = m["market_cap"]["usd"]
    value_now   = INVEST_AMOUNT * (1 + price_pct/100)

    # 2) fetch yesterday 24 h volume
    vol_yesterday = get_yesterday_volume(token_id, now)
    if vol_yesterday and vol_yesterday>0:
        vol_diff_pct = (vol_today - vol_yesterday) / vol_yesterday * 100
        vol_trend = f"[{vol_diff_pct:+.1f}%]"
    else:
        vol_trend = "[N/A]"

    # 3) price emoji
    if price_pct >= 10:   emoji = "🔥"
    elif price_pct >= 3:  emoji = "📈"
    elif price_pct <= -10: emoji = "💀"
    elif price_pct <= -3: emoji = "📉"
    else:                 emoji = ""

    # 4) compose tweet
    tweet = (
        f"DEGEN DAILY — ft. ${token_name.lower()} {twitter_handle}\n\n"
        f"$100 → ${value_now:,.2f} [{price_pct:+.2f}%] {emoji}\n\n"
        f"🏷️ Price: ${format_price_dynamic(price)} | Market Cap: ${mcap/1e6:.1f}M\n"
        f"↕️ ATL ↑ {abs(atl_chg):.0f}% | ATH ↓ {abs(ath_chg):.0f}%\n"
        f"🔊 Volume [24h]: ${vol_today/1e6:.1f}M {vol_trend}\n\n"
        f"New breakdown same time tomorrow!"
    )

    print("📤 Tweet content:")
    print(tweet)

    # 5) dispatch
    res = requests.post(os.environ["IFTTT_WEBHOOK_URL"], json={"value1": tweet})
    print("✅ Tweet sent!" if res.ok else f"⚠️ IFTTT error: {res.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")
