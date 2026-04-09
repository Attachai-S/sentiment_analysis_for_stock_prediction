import os
import time
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import yfinance as yf

# SYMBOLS = ["AAPL","MSFT"] #for testing
SYMBOLS = ["AAPL", "CSCO", "INTC", "MSFT", "NVDA","ORCL"]
USER_TYPE = "personal" # or "university"
START_DATE = "2025-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")


load_dotenv()
API_KEY = os.getenv("FINNHUB_API_KEY") 
START_DATE = "2025-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")
RESOLUTION = "D" # D = daily, W = weekly, M = monthly

def selected_path(task,symbol, user_type):
    sav_stock_data_personal = f"stock_collection/stock_dataset/stock_{symbol}.csv"
    sav_stock_data_university = f"../stock_collection/stock_dataset/stock_{symbol}.csv"
    if task == "save": 
        if user_type == "personal": return sav_stock_data_personal
        elif user_type == "university": return sav_stock_data_university

def line(option="none", symbol=""):
    if option == "start": print(f"\n{'=' * 50}\n start get stock data of {symbol} \n{'=' * 50}\n")
    elif option == "end": print(f"\n{'=' * 50}\n end get stock data of {symbol} \n{'=' * 50}\n")
    else: print(f"\n{'=' * 50}\n")

def get_stock_data(symbol):
    line("start", symbol)
    stock = yf.Ticker(symbol)
    _df = stock.history(start=START_DATE, end=END_DATE, interval="1d")
    if _df.empty:
        print(f"⚠️ No data {symbol} in this moment(s)")
        return
    
    _df = _df.reset_index()
    
    _df['Date'] = pd.to_datetime(_df['Date']).dt.date
    
    # เลือกเฉพาะคอลัมน์ที่จำเป็น (OHLCV)
    _df = _df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    
    # เรียงลำดับวันที่จากเก่าไปใหม่
    _df = _df.sort_values(by="Date", ascending=True)
    
    _df.to_csv(selected_path("save",symbol,USER_TYPE), index=False, encoding='utf-8')
    
    print(f"save {symbol} total {len(_df)} day(s)")
    print(f"Start {_df['Date'].iloc[0]} to {_df['Date'].iloc[-1]}")

    line("end", symbol)

for symbol in SYMBOLS:
    get_stock_data(symbol)