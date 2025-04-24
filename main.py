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
    "FITCOIN": ("fitcoin-2", "@itsfitcoin"),
}

INVEST_AMOUNT = 100

force_token = os.getenv("FORCE_TOKEN")
token_keys = list(tokens.keys())

if force_token and force_token in tokens:
    token_name = force_token
else:
    now = datetime.datetime.utcnow()
    token_name = token_keys[now.hour % len(token_keys)]

token_id, twitter_handle = tokens[token_name]

def format_price_dynamic(p):
    if p >= 1:
        return f"{p:.3f}"
    s = f"{p:.12f}"
    dec = s.split(".")[1]
    nz = next((i for i, c in enumerate(dec) if c != "0"), len(dec))
    digits = dec[nz:nz+3]
    return f"0.{dec[:nz]}{digits}"

def format_mcap(m):
    return f"${m/1e9:.1f}B" if m >= 1e9 else f"${m/1e6:.1f}M"

def get_circumstantial_text(price_pct, vol_diff_pct):
    if price_pct > 0 and vol_diff_pct > 0:
        if price_pct > vol_diff_pct:
            return "Momentum Move"
        else:
            return "Accumulation"
    elif price_pct > 0 and vol_diff_pct < 0:
        if price_pct > abs(vol_diff_pct):
            return "Weak Rally"
        else:
            return "Anemic Rally"
    elif price_pct < 0 and vol_diff_pct > 0:
        if abs(price_pct) > vol_diff_pct:
            return "Supply Flush"
        else:
            return "Distribution"
    elif price_pct < 0 and vol_diff_pct < 0:
        if abs(price_pct) > abs(vol_diff_pct):
            return "Decay Trend"
        else:
            return "Dry Bleed"
    return "Unknown"

def get_call_text(pattern_text, price_pct, vol_diff_pct):
    if "Momentum Move" in pattern_text and abs(price_pct) >= 2:
        return "LONG — Momentum Move"
    elif "Accumulation" in pattern_text:
        threshold = min(price_pct * 2, 10)
        if vol_diff_pct > threshold and abs(price_pct) >= 2:
            return "LONG — Accumulation"
        else:
            return "NOTHING — Accumulation (weak)"
    elif "Dry Bleed" in pattern_text:
        if abs(vol_diff_pct) > abs(price_pct) * 1.4 and abs(price_pct) >= 2:
            return "SHORT — Dry Bleed"
        else:
            return "NOTHING — Dry Bleed (weak)"
    elif pattern_text in ["Decay Trend", "Distribution", "Weak Rally", "Anemic Rally"]:
        return f"NOTHING — {pattern_text} (uncertain)"
    return "NOTHING — Unknown (uncertain)"

try:
    r = requests.get(f"https://api.coingecko.com/api/v3/coins/{token_id}")
    m = r.json()["market_data"]

    price = m["current_price"]["usd"]
    price_pct = m["price_change_percentage_24h"]
    mcap = m["market_cap"]["usd"]
    value_now = INVEST_AMOUNT * (1 + price_pct / 100)

    chart = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart",
        params={"vs_currency": "usd", "days": 1}
    ).json().get("total_volumes", [])

    if chart:
        start_vol = chart[0][1]
        end_vol = chart[-1][1]
        if start_vol > 0:
            vol_diff_pct = (end_vol - start_vol) / start_vol * 100
            vol_trend = f"[{vol_diff_pct:+.1f}%]"
            pattern_text = get_circumstantial_text(price_pct, vol_diff_pct)
            call_text = get_call_text(pattern_text, price_pct, vol_diff_pct)
            circum_text = f"\n\n🎯 {call_text}"
        else:
            vol_trend = "[N/A]"
            circum_text = "\n\n🎯 UNKNOWN"
    else:
        vol_trend = ""
        circum_text = "\n\n🎯 UNKNOWN"

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
        f"DEGEN DAILY — ft. ${token_name.lower()} {twitter_handle}\n\n"
        f"$100 → ${value_now:,.2f} [{price_pct:+.2f}%] {emoji}\n\n"
        f"🏷️ Price: ${format_price_dynamic(price)} | Market Cap: {format_mcap(mcap)}\n"
        f"🔊 Volume [24h]: ${end_vol/1e6:.1f}M {vol_trend}"
        f"{circum_text}"
    )

    print("📤 Tweet content:")
    print(tweet)

    res = requests.post(os.environ["IFTTT_WEBHOOK_URL"], json={"value1": tweet})
    print("✅ Tweet sent!" if res.ok else f"⚠️ IFTTT error: {res.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")
