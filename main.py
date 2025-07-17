import requests
import datetime
import os

# ✅ Tokens dictionary
tokens = {
    "WIF":       ("dogwifcoin", "@dogwifcoin"),
    "BONK":      ("bonk", "@bonk_inu"),
    "POPCAT":    ("popcat", "@POPCATSOLANA"),
    "TRUMP":     ("official-trump", "@GetTrumpMemes"),
    "TITCOIN":   ("titcoin-2", "@TheTitCoin"),
    "FARTCOIN":  ("fartcoin", "@FartCoinOfSOL"),
    "PAIN":      ("pain", "@pain"),
    "MEW":       ("cat-in-a-dogs-world", "@mew"),
    "AI16Z":     ("ai16z", "@aixvc_agent"),
    "PNUT":      ("peanut-the-squirrel", "@pnutsolana"),
    "RFC":       ("retard-finder-coin", "@RFindercoin"),
    "FWOG":      ("fwog", "@itsafwog"),
    "AURA":      ("aura-on-sol", "@auracoinsolana"),
    "MOODENG":   ("moo-deng", "@MooDengSOL"),
    "WEN":       ("wen-4", "@wenwencoin"),
    "ZEREBRO":   ("zerebro", "@0xzerebro"),
    "USELESS":   ("useless-3", "@theuselesscoin"),
    "SLERF":     ("slerf", "@Slerfsol"),
    "PUMP":      ("pump-fun", "@pumpdotfun"),
    "UFD":       ("unicorn-fart-dust", "@BasementRon"),
    "PENGU":     ("pudgy-penguins", "@pudgypenguins"),
    "GIGACHAD":  ("gigachad-2", "@gigachad"),
    "PONKE":     ("ponke", "@ponkesol"),
    "GOAT":      ("goatseus-maximus", "@gospelofgoatse"),
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

print(f"🕐 Bot running | Selected token: ${token_name} ({token_id})")

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
        end_vol = chart[-1][1]
        vol_trend = f"${end_vol/1e6:.1f}M"
    else:
        vol_trend = "N/A"

    tweet = (
        f"DEGEN DAILY — ft. ${token_name.lower()} {twitter_handle}\n\n"
        f"$100 → ${value_now:,.2f} [{price_pct:+.2f}%] (24h)\n\n"
        f"🏷️ Price: ${format_price_dynamic(price)} | Market Cap: {format_mcap(mcap)}\n"
        f"🔊 Volume: {vol_trend} (24h)"
    )

    print("📤 Tweet content:")
    print(tweet)

    res = requests.post(os.environ["IFTTT_WEBHOOK_URL"], json={"value1": tweet})
    print("✅ Tweet sent!" if res.ok else f"⚠️ IFTTT error: {res.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")
