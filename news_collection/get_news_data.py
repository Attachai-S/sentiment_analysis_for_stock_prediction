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
# SYMBOLS = ["ATTCH"]

REQUEST_SLEEP = 1.2 # พักทุก request
SYMBOL_SLEEP = 60 # พักหลังจบ 1 symbol = 1.00 นาที
MAX_RETRIES = 5 # จำนวนครั้ง retry เมื่อเจอ 429

USER_TYPE = "personal" # or "university"
def selected_path(symbol, user_type="personal"):
    write_personal_path = f"news_collection/news_dataset/news_{symbol}.csv"
    write_university_path = f"../news_collection/news_dataset/news_{symbol}.csv"
    
    if user_type == "personal": return write_personal_path
    elif user_type == "university": return write_university_path


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
    start_date = date(2026, 4, 1)# year, month, day
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
    
    df.to_csv(selected_path(symbol, USER_TYPE), index=False, encoding='utf-8')
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

# get_news_dataset()
if __name__ == "__main__":
    get_news_dataset()
    
def auto_pipline_get_news_dataset(symbol):
    print(f"\n🚀 [PIPELINE] Start get news data : {symbol}")
    try:
        # 1. เรียกใช้ฟังก์ชันเดิมของคุณที่ทำหน้าที่ดึงข่าวของ 1 หุ้น
        start_get_news_data(symbol)
        
        # 2. ตรวจสอบความสำเร็จ (เช็คว่าไฟล์ถูกสร้างขึ้นมาจริงๆ หรือไม่)
        # ใช้ฟังก์ชัน selected_path ที่มีอยู่ในไฟล์นี้อยู่แล้วเพื่อดึง path ของไฟล์
        file_path = selected_path(symbol, USER_TYPE)
        
        if os.path.exists(file_path):
            print(f"[PIPELINE] Finished, save on: {file_path}")
            return True
        else:
            print(f"[PIPELINE] call data finished but no file found (may have no news in this period)")
            return False
            
    except Exception as e:
        print(f"[PIPELINE] เกิดข้อผิดพลาดในการดึงข่าว {symbol}: {e}")
        return False