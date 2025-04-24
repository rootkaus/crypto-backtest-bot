import pandas as pd
import re
import requests
import os
from datetime import datetime

# --- CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0mLZ_7hNYPquqsiLe9YUADHka8V1Lf5b4OelUc-8BP9H31aLgoC9p30UlXYLKov2Fcbr_qWHlHT21/pub?gid=0&single=true&output=csv"
IFTTT_ACCURACY_URL = os.getenv("IFTTT_ACCURACY_URL")

# --- Helpers ---
def extract_token(text):
    m = re.search(r"ft\. \$(\w+)", str(text))
    return m.group(1).upper() if m else None

def extract_price(text):
    m = re.search(r"Price: \$([\d.]+)", str(text))
    return float(m.group(1)) if m else None

def extract_call(text):
    text = str(text).upper()
    if "LONG" in text or "BUY" in text:
        return "LONG"
    elif "SHORT" in text or "SELL" in text:
        return "SHORT"
    elif "NOTHING" in text:
        return "NOTHING"
    return None

# --- Load and format ---
df = pd.read_csv(CSV_URL, header=None)
df.columns = ['Timestamp', 'Handle', 'Tweet content', 'Link']
df['Date'] = pd.to_datetime(df['Timestamp'], errors='coerce')
df['Token'] = df['Tweet content'].apply(extract_token)
df['Price'] = df['Tweet content'].apply(extract_price)
df['Call'] = df['Tweet content'].apply(extract_call)
df = df.dropna(subset=['Date', 'Token', 'Price'])
df = df.sort_values(by='Date')

# --- Exit if empty ---
if df.empty:
    print("❌ No entries to analyze.")
    exit()

# --- Get latest ---
latest = df.iloc[-1]
token = latest['Token']
call = latest['Call']
price_now = latest['Price']
date_now = latest['Date']

# --- Find prior actionable call ---
prev_df = df[(df['Token'] == token) & (df['Date'] < date_now)]
prev_actionable = prev_df[prev_df['Call'].isin(['LONG', 'SHORT'])]
if prev_actionable.empty:
    print(f"⚠️ No prior LONG/SHORT call for ${token} — tracking anyway.")
    result = "❓"
    pct_str = "N/A"
else:
    prev = prev_actionable.iloc[-1]
    price_prev = prev['Price']
    prev_call = prev['Call']
    pct_change = ((price_now - price_prev) / price_prev) * 100
    pct_str = f"{pct_change:+.2f}%"

    # --- Evaluate result ---
    if prev_call == "LONG":
        result = "✅" if pct_change > 0 else "❌"
    else:
        result = "✅" if pct_change < 0 else "❌"

# --- Send to IFTTT ---
payload = {
    "value1": token,
    "value2": call or "UNKNOWN",
    "value3": f"{result} ({pct_str})"
}

try:
    r = requests.post(IFTTT_ACCURACY_URL, json=payload)
    if r.ok:
        print(f"✅ Sent to IFTTT: {payload}")
    else:
        print(f"⚠️ IFTTT error: {r.status_code} — {r.text}")
except Exception as e:
    print(f"❌ Error sending to IFTTT: {e}")
