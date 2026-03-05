import requests
import pandas as pd
from datetime import date, timedelta

API_KEY = ""
symbol = "AAPL"
def get_news(symbol):
    to_date = date.today()
    from_date = to_date - timedelta(days=365)

    url = "https://finnhub.io/api/v1/company-news"
    params = {
        "symbol": symbol,
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
    }

    headers = {"X-Finnhub-Token": API_KEY}  # Finnhub รองรับ header นี้ :contentReference[oaicite:3]{index=3}
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    news = r.json()

    print("items:", len(news))
    print(news[0].keys() if news else "no news")

    save_csv

###### Save to CSV
def save_csv(news, symbol):
    df = pd.DataFrame(news)

    # แปลงเวลา unix -> datetime (datetime เป็นวินาที)
    if "datetime" in df.columns:
        df["published_at"] = pd.to_datetime(df["datetime"], unit="s", utc=True)

    df["ticker"] = symbol

    keep_cols = [c for c in ["ticker", "published_at", "headline", "summary", "source", "url"] if c in df.columns]
    df = df[keep_cols]

    df.to_csv(f"news_collection/news_{symbol}.csv", index=False, encoding="utf-8-sig")
    print("saved:", f"news_{symbol}.csv")