import requests
import pandas as pd
import time
from datetime import datetime

packages = [
    "agora-rtc-sdk-ng",
    "agora-rtc-sdk",
    "agora-rtm-sdk",
    "agora-rtc-react",
    "react-native-agora",
    "agora-agent-server-sdk",
    "agora-agent-client-toolkit",
    "agora-agent-uikit",
    "agora-conversational-ai-denoiser"
]

def fetch_downloads(package, start_year=2015, end_year=2024):
    all_data = []
    for year in range(start_year, end_year + 1):
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        url = f"https://api.npmjs.org/downloads/range/{start_date}:{end_date}/{package}"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            if 'downloads' in data and data['downloads']:
                all_data.extend(data['downloads'])
        time.sleep(0.5) # rate limiting

    if not all_data:
        return pd.Series(dtype=float)

    df = pd.DataFrame(all_data)
    df['day'] = pd.to_datetime(df['day'])
    df = df.set_index('day')
    # Resample to weekly, starting on Monday ('W-MON')
    weekly = df['downloads'].resample('W-MON').sum()
    return weekly

results = {}
for pkg in packages:
    print(f"Fetching {pkg}...")
    results[pkg] = fetch_downloads(pkg)

df_all = pd.DataFrame(results)

if "agora-rtc-sdk-ng" in df_all.columns and "agora-rtc-sdk" in df_all.columns:
    df_all["rtc-sdk-total"] = df_all["agora-rtc-sdk-ng"].fillna(0) + df_all["agora-rtc-sdk"].fillna(0)

# Reorder columns
cols = ["agora-rtc-sdk-ng", "agora-rtc-sdk", "rtc-sdk-total", "agora-rtm-sdk", "agora-rtc-react", "react-native-agora", "agora-agent-server-sdk", "agora-agent-client-toolkit", "agora-agent-uikit", "agora-conversational-ai-denoiser"]

for c in cols:
    if c not in df_all.columns:
        df_all[c] = 0

df_all = df_all[cols]
df_all.index.name = 'Date'

# Save to CSV
df_all.to_csv("npm_downloads_weekly.csv")
print("Data saved to npm_downloads_weekly.csv")
