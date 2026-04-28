import os
import pandas as pd
from datetime import datetime
import sys
import yfinance as yf
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from news_collection.get_news_data import auto_pipline_get_news_dataset
from stock_collection.get_stock_data import auto_pipline_get_stock_dataset
from news_collection.text_processing import auto_pipline_text_processor
from news_collection.sentiment_scoring import auto_pipline_sentiment_scorer
from data_merged.data_merging import auto_pipline_data_merger
from LLM_model import run_daily_update

BASE_PATH = "news_collection/news_dataset"

# ===== main page logic =====
def get_symbols():
    if not os.path.exists(BASE_PATH):
        return []

    files = os.listdir(BASE_PATH)

    # print(f"Files in {BASE_PATH}: {files}")  # Debug: แสดงไฟล์ทั้งหมดในโฟลเดอร์
    symbols = []
    for file in files:
        if file.startswith("news_") and file.endswith(".csv"):
            symbol = file.replace("news_", "").replace(".csv", "")
            symbols.append(symbol)

    return symbols
# ===== main page logic =====
# ===== check page logic =====
def get_latest_date(file_path, column_name):
    try:
        df = pd.read_csv(file_path)

        if df.empty:
            return None

        latest = pd.to_datetime(df[column_name]).max()
        return latest.date()

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None
    
def is_recent(date, days=2):
    if date is None:
        return False
    today = datetime.today().date()
    return (today - date).days <= days


def is_data_up_to_date(symbol):

    news_path = f"news_collection/news_dataset/news_{symbol}.csv"
    stock_path = f"stock_collection/stock_dataset/stock_{symbol}.csv"
    llm_path = f"data_merged/{symbol}_gemini_results.csv"

    if not os.path.exists(news_path) or not os.path.exists(stock_path) or not os.path.exists(llm_path):
        return False

    news_date = get_latest_date(news_path, "published_at")
    stock_date = get_latest_date(stock_path, "Date")
    llm_date = get_latest_date(llm_path, "Date")

    print("DEBUG dates:", news_date, stock_date, llm_date)

    return (
        is_recent(news_date, 1) and
        is_recent(stock_date, 3) and
        is_recent(llm_date, 1)
    )

def run_full_pipeline(symbol):

    news_path = f"news_collection/news_dataset/news_{symbol}.csv"
    stock_path = f"stock_collection/stock_dataset/stock_{symbol}.csv"
    llm_path = f"data_merged/{symbol}_gemini_results.csv"

    # 🔹 News
    if not os.path.exists(news_path):
        auto_pipline_get_news_dataset(symbol)

    # 🔹 Stock
    if not os.path.exists(stock_path):
        auto_pipline_get_stock_dataset(symbol)

    # 🔹 LLM (หนักสุด → เช็คดี ๆ)
    if not os.path.exists(llm_path):
        auto_pipline_text_processor(symbol)
        auto_pipline_sentiment_scorer(symbol)
        auto_pipline_data_merger(symbol)
        run_daily_update(symbol)

    print("run pipeline done")
# ===== check page logic =====
# ===== search ui logic =====
def is_valid_symbol(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")

        return not data.empty
    except:
        return False
# ===== search ui logic =====
# ===== results page logic =====
def load_prediction(symbol):
    path = f"data_merged/{symbol}_gemini_results.csv"

    if not os.path.exists(path):
        return None

    df = pd.read_csv(path)
    df = df.sort_values("Date", ascending=False)

    return df.head(10)
# ===== results page logic =====

