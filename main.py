updated_script = """
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
    nz = next((i for i, c in enumerate(dec) if c != "0"), len(dec))
    digits = dec[nz:nz+3]
    return f"0.{dec[:nz]}{digits}"

def get_circumstantial_text(price_pct, vol_diff_pct):
    if price_pct > 0 and vol_diff_pct > 0:
        if price_pct > vol_diff_pct:
            return "Price 🔺 > Volume 🔺 = Controlled Uptrend"
        else:
            return "Volume 🔺 > Price 🔺 = Accumulation Phase"
    elif price_pct > 0 and vol_diff_pct < 0:
        if price_pct > abs(vol_diff_pct):
            return "Price 🔺 > Volume 🔻 = Low-Conviction Pump"
        else:
            return "Volume 🔻 > Price 🔺 = Fragile Push"
    elif price_pct < 0 and vol_diff_pct > 0:
        if abs(price_pct) > vol_diff_pct:
            return "Price 🔻 > Volume 🔺 = Supply Flush"
        else:
            return "Volume 🔺 > Price 🔻 = Reactive Interest"
    elif price_pct < 0 and vol_diff_pct < 0:
        if abs(price_pct) > abs(vol_diff_pct):
            return "Price 🔻 > Volume 🔻 = Soft Decline"
        else:
            return "Volume 🔻 > Price 🔻 = Dry Bleed"
    else:
        return ""

def get_call_text(pattern_text, price_pct, vol_diff_pct):
    if abs(price_pct) < 2.99 or abs(price_pct - vol_diff_pct) < 3:
        return "NOTHING"
    elif "Controlled Uptrend" in pattern_text:
        return "BUY"
    elif "Dry Bleed" in pattern_text:
        return "SELL"
    else:
        return "NOTHING"

try:
    r = requests.get(f"https://api.coingecko.com/api/v3/coins/{token_id}")
    m = r.json()["market_data"]

    price       = m["current_price"]["usd"]
    price_pct   = m["price_change_percentage_24h"]
    vol_today   = m["total_volume"]["usd"]
    mcap        = m["market_cap"]["usd"]
    value_now   = INVEST_AMOUNT * (1 + price_pct / 100)

    chart = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart",
        params={"vs_currency": "usd", "days": 1}
    ).json().get("total_volumes", [])
    if chart:
        start_vol = chart[0][1]
        end_vol   = chart[-1][1]
        if start_vol > 0:
            vol_diff_pct = (end_vol - start_vol) / start_vol * 100
            vol_trend = f"[{vol_diff_pct:+.1f}%]"
            pattern_text = get_circumstantial_text(price_pct, vol_diff_pct)
            call_text = get_call_text(pattern_text, price_pct, vol_diff_pct)
            circum_text = f"\\n\\n🧠 {pattern_text}\\n🎯 Call: {call_text}"
        else:
            vol_trend = "[N/A]"
            circum_text = ""
    else:
        vol_trend = ""
        circum_text = ""

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

    tweet = (
        f"DEGEN DAILY — ft. ${token_name.lower()} {twitter_handle}\\n\\n"
        f"$100 → ${value_now:,.2f} [{price_pct:+.2f}%] {emoji}\\n\\n"
        f"🏷️ Price: ${format_price_dynamic(price)} | Market Cap: ${mcap/1e6:.1f}M\\n"
        f"🔊 Volume [24h]: ${vol_today/1e6:.1f}M {vol_trend}"
        f"{circum_text}"
    )

    print("📤 Tweet content:")
    print(tweet)

    res = requests.post(os.environ["IFTTT_WEBHOOK_URL"], json={"value1": tweet})
    print("✅ Tweet sent!" if res.ok else f"⚠️ IFTTT error: {res.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")
