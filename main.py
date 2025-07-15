import requests
import datetime
import os

tokens = {
    "WIF": ("dogwifcoin", "@dogwifcoin", "https://maker.ifttt.com/trigger/post_wif/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "BONK": ("bonk", "@bonk_inu", "https://maker.ifttt.com/trigger/post_bonk/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "POPCAT": ("popcat", "@POPCATSOLANA", "https://maker.ifttt.com/trigger/post_popcat/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "TRUMP": ("official-trump", "@GetTrumpMemes", "https://maker.ifttt.com/trigger/post_trump/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "TITCOIN": ("titcoin-2", "@TheTitCoin", "https://maker.ifttt.com/trigger/post_titcoin/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "FARTCOIN": ("fartcoin", "@FartCoinOfSOL", "https://maker.ifttt.com/trigger/post_fartcoin/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "PAIN": ("pain", "@pain", "https://maker.ifttt.com/trigger/post_pain/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "MEW": ("cat-in-a-dogs-world", "@mew", "https://maker.ifttt.com/trigger/post_mew/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "AI16Z": ("ai16z", "@aixvc_agent", "https://maker.ifttt.com/trigger/post_ai16z/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "PNUT": ("peanut-the-squirrel", "@pnutsolana", "https://maker.ifttt.com/trigger/post_pnut/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "RFC": ("retard-finder-coin", "@RFindercoin", "https://maker.ifttt.com/trigger/post_rfc/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "FWOG": ("fwog", "@itsafwog", "https://maker.ifttt.com/trigger/post_fwog/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "AURA": ("aura-on-sol", "@auracoinsolana", "https://maker.ifttt.com/trigger/post_aura/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "MOODENG": ("moo-deng", "@MooDengSOL", "https://maker.ifttt.com/trigger/post_moodeng/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "WEN": ("wen-4", "@wenwencoin", "https://maker.ifttt.com/trigger/post_wen/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "ZEREBRO": ("zerebro", "@0xzerebro", "https://maker.ifttt.com/trigger/post_zerebro/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "USELESS": ("useless-3", "@theuselesscoin", "https://maker.ifttt.com/trigger/post_useless/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "SLERF": ("slerf", "@Slerfsol", "https://maker.ifttt.com/trigger/post_slerf/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "PUMP": ("pump-fun", "@pumpdotfun", "https://maker.ifttt.com/trigger/post_pump/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "UFD": ("unicorn-fart-dust", "@BasementRon", "https://maker.ifttt.com/trigger/post_ufd/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "PENGU": ("pudgy-penguins", "@pudgypenguins", "https://maker.ifttt.com/trigger/post_pengu/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "GIGACHAD": ("gigachad-2", "@Gigachad", "https://maker.ifttt.com/trigger/post_gigachad/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "PONKE": ("ponke", "@ponkesol", "https://maker.ifttt.com/trigger/post_ponke/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"),
    "GOAT": ("goatseus-maximus", "@gospelofgoatse", "https://maker.ifttt.com/trigger/post_goat/json/with/key/cLcVxJK2s0I_FF-5UNwjNq")
}

INVEST_AMOUNT = 100

force_token = os.getenv("FORCE_TOKEN")
token_keys = list(tokens.keys())

if force_token and force_token in tokens:
    token_name = force_token
else:
    now = datetime.datetime.utcnow()
    token_name = token_keys[now.hour % len(token_keys)]

token_id, twitter_handle, webhook_url = tokens[token_name]

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
        f"$100 → ${value_now:,.2f} [{price_pct:+.2f}%]\n\n"
        f"🏷️ Price: ${format_price_dynamic(price)} | Market Cap: {format_mcap(mcap)}\n"
        f"🔊 Volume [24h]: {vol_trend}"
    )

    print("📤 Tweet content:")
    print(tweet)

    res = requests.post(webhook_url, json={"JsonPayload": tweet})
    print("✅ Tweet sent!" if res.ok else f"⚠️ IFTTT error: {res.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")
