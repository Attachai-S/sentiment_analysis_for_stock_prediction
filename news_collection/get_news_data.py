import os
import time
import pandas as pd
from dotenv import load_dotenv
import requests
from datetime import date, timedelta

load_dotenv()
API_KEY = os.getenv("FINNHUB_API_KEY") 
BASE_URL = "https://finnhub.io/api/v1/company-news"
SYMBOLS = ["AAPL", "CSCO", "INTC", "MSFT", "NVDA","ORCL"]

REQUEST_SLEEP = 1.2 # พักทุก request
SYMBOL_SLEEP = 72 # พักหลังจบ 1 symbol = 1.20 นาที
MAX_RETRIES = 5 # จำนวนครั้ง retry เมื่อเจอ 429

def fetch_news_with_retry(params):
    for attempt in range(MAX_RETRIES):
        response = requests.get(BASE_URL, params=params, timeout=30)

        if response.status_code == 429:
            wait_time = 10 * (attempt + 1)
            print(f"429 Too Many Requests -> wait {wait_time} seconds and retry...")
            time.sleep(wait_time)
            continue

        response.raise_for_status()
        return response.json()

    raise Exception("Failed after retries because of rate limit.")

def start_get_news_data(symbol):
    start_date = date(2025, 1, 1)
    end_date = date.today()
    window_days = 7

    all_news = []
    current_date = start_date

    while current_date <= end_date:
        next_date = min(current_date + timedelta(days=window_days - 1), end_date)

        params = {
            "symbol": symbol,
            "from": current_date.isoformat(),
            "to": next_date.isoformat(),
            "token": API_KEY
        }

        news = fetch_news_with_retry(params)

        all_news.extend(news)

        print(
            f"{symbol} {current_date} -> {next_date} : "
            f"{len(news)} news, total {symbol} news : {len(all_news)}"
        )

        # พักทุก request เพื่อคุม call rate
        time.sleep(REQUEST_SLEEP)

        current_date = next_date + timedelta(days=1)

    df = pd.DataFrame(all_news)

    if df.empty:
        print(symbol, "no news")
        return

    df["published_at"] = pd.to_datetime(df["datetime"], unit="s", utc=True)
    df["ticker"] = symbol

    df = df[["ticker", "published_at", "headline", "summary", "source", "url"]]
    df = df.drop_duplicates(subset="url")
    df = df.sort_values("published_at")
    
    # df.to_csv(r"\news_collection\news_dataset\news_{symbol}.csv}", index=False)
    # df.to_csv(f"/news_dataset/news_{symbol}.csv", index=False)
    df.to_csv(f"../news_collection/news_dataset/news_{symbol}.csv", index=False)

    print("saved:", symbol, len(df), "rows")

def get_news_dataset() : 
    for symbol in SYMBOLS:
        start_get_news_data(symbol)
        if symbol != SYMBOLS[-1]:
            print(f"Finished {symbol}, sleeping for {SYMBOL_SLEEP} seconds...")
            time.sleep(SYMBOL_SLEEP)
            print(f"Starting next \"{symbol}\" symbol...")
        else:
            print("All symbols processed.")

get_news_dataset()