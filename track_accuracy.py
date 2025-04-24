import pandas as pd
import re
import requests
from datetime import datetime

# --- CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0mLZ_7hNYPquqsiLe9YUADHka8V1Lf5b4OelUc-8BP9H31aLgoC9p30UlXYLKov2Fcbr_qWHlHT21/pub?gid=0&single=true&output=csv"
IFTTT_WEBHOOK_URL = "https://maker.ifttt.com/trigger/call_result/json/with/key/cLcVxJK2s0I_FF-5UNwjNq"

# --- Helper functions ---
def extract_token(text):
    m = re.search(r"ft\. \$(\w+)", str(text))
    return m.group(1).upper() if m else None

def extract_price(text):
    m = re.search(r"Price: \$([\d.]+)", str(text))
    return float(m.group(1)) if m else None

def extract_call(text):
    if "LONG" in text:
        return "LONG"
    elif "SHORT" in text:
        return "SHORT"
    return None

# --- Step 1: Load and parse the sheet ---
df = pd.read_csv(CSV_URL)
df['Date'] = pd.to_datetime(df['Timestamp'], errors='coerce')
df['Token'] = df['Tweet content'].apply(extract_token)
df['Price'] = df['Tweet content'].apply(extract_price)
df['Call'] = df['Tweet content'].apply(extract_call)
df = df.dropna(subset=['Date', 'Token', 'Price', 'Call'])
df = df.sort_values(by='Date')

# --- Step 2: Get the latest call ---
latest = df.iloc[-1]
token = latest['Token']
call = latest['Call']
price_now = latest['Price']
date_now = latest['Date']

# --- Step 3: Find previous price for this token ---
prev_df = df[(df['Token'] == token) & (df['Date'] < date_now)]
if prev_df.empty:
    print("❌ No previous data for this token — skipping")
else:
    prev = prev_df.iloc[-1]
    price_prev = prev['Price']
    pct_change = ((price_now - price_prev) / price_prev) * 100
    pct_str = f"{pct_change:+.2f}%"

    # --- Step 4: Determine result ---
    if call == "LONG":
        result = "✅" if pct_change > 0 else "❌"
    else:
        result = "✅" if pct_change < 0 else "❌"

    # --- Step 5: Send to IFTTT ---
    payload = {
        "value1": token,
        "value2": call,
        "value3": f"{result} ({pct_str})"
    }

    try:
        r = requests.post(IFTTT_WEBHOOK_URL, json=payload)
        if r.ok:
            print(f"✅ Sent to IFTTT: {payload}")
        else:
            print(f"⚠️ IFTTT error: {r.status_code} — {r.text}")
    except Exception as e:
        print(f"❌ Error sending to IFTTT: {e}")
