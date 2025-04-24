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

# --- Load ---
df = pd.read_csv(CSV_URL, header=None)
df.columns = ['Timestamp', 'Handle', 'Tweet content', 'Link']
df['Date'] = pd.to_datetime(df['Timestamp'], errors='coerce')
df['Token'] = df['Tweet content'].apply(extract_token)
df['Price'] = df['Tweet content'].apply(extract_price)
df['Call'] = df['Tweet content'].apply(extract_call)

df = df.dropna(subset=['Date', 'Token', 'Price'])
df = df.sort_values(by='Date')

# Only evaluate actual positions — LONG or SHORT
positions = df[df['Call'].isin(['LONG', 'SHORT'])]

if positions.empty:
    print("❌ No actionable positions found.")
    exit()

# Get the latest actionable position
latest = positions.iloc[-1]
token = latest['Token']
call = latest['Call']
price_entry = latest['Price']
date_entry = latest['Date']

# Find the next available row for same token — ANY call (LONG, SHORT, NOTHING)
exit_df = df[(df['Token'] == token) & (df['Date'] > date_entry)]
if exit_df.empty:
    print(f"⚠️ No exit price found for ${token} — waiting for next log.")
    exit()

exit_price = exit_df.iloc[0]['Price']
pct_change = ((exit_price - price_entry) / price_entry) * 100
pct_str = f"{pct_change:+.2f}%"

# Determine if the call was correct
if call == "LONG":
    result = "✅" if pct_change > 0 else "❌"
else:
    result = "✅" if pct_change < 0 else "❌"

# Send to IFTTT
payload = {
    "value1": token,
    "value2": call,
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
