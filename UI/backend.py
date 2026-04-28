import os
import glob
import flet as ft
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from LLM_model import run_daily_update
from news_collection.get_news_data import auto_pipline_get_news_dataset
from news_collection.text_processing import auto_pipline_text_processor
from news_collection.sentiment_scoring import auto_pipline_sentiment_scorer
from stock_collection.get_stock_data import auto_pipline_get_stock_dataset
from data_merged.data_merging import auto_pipline_data_merger

def curr_route(page : ft.Page):
    print("Current route:", page.route)

class AppState:
    def __init__(self):
        self.selected_symbol = ""

app_state = AppState()

BASE_PATH = "news_collection/news_dataset/" 

def get_existing_stocks():
    if not os.path.exists(BASE_PATH):
        return []
    
    # ค้นหาไฟล์ที่ชื่อขึ้นต้นด้วย news_ และลงท้ายด้วย .csv
    files = glob.glob(os.path.join(BASE_PATH, "news_*.csv"))
    
    symbols = []
    for file_path in files:
        # แยกเฉพาะชื่อไฟล์ออกมา เช่น news_AAPL.csv
        file_name = os.path.basename(file_path)
        # ตัดคำว่า news_ และ .csv ออก เพื่อให้เหลือแค่ AAPL
        symbol = file_name.replace("news_", "").replace(".csv", "")
        symbols.append(symbol)
        
    return symbols

# //////////////////////////

# def get_news_dataset(symbol): print("get news dataset")

def get_paths(symbol):
    return {
        "news":f"news_collection/news_dataset/news_{symbol}.csv",
        "stock":f"stock_checking/stock_dataset/stock_{symbol}.csv",
        # "processed":f"news_collection/news_processed/news_{symbol}_cleaned.csv",
        # "news":f"news_collection/news_sentiment/news_{symbol}_sentiment.csv",
        "processed":f"news_collection/news_sentiment/sentiment_data/{symbol}_matching_fixed.csv",
        "sentiment":f"news_collection/scored_data/{symbol}_scored.csv",
        "merged":f"data_merged/merged_{symbol}.csv",
        "llm":f"data_merged/merged_{symbol}_gemini_results.csv",
    }

def check_all_files(symbol):
    paths = get_paths(symbol)
    status = {}

    for key, path in paths.items():
        status[key] = os.path.exists(path)

    return status

from LLM_model import run_daily_update

def run_pipline_step(symbol, step):
    try:
        if step == "news":
            return auto_pipline_get_news_dataset(symbol)

        elif step == "stock":
            return auto_pipline_get_stock_dataset(symbol)

        elif step == "processed":
            return auto_pipline_text_processor(symbol)

        elif step == "sentiment":
            return auto_pipline_sentiment_scorer(symbol)

        elif step == "merged":
            return auto_pipline_data_merger(symbol)

        elif step == "llm":
            return run_daily_update(symbol)

    except Exception as e:
        print(f"[ERROR] step {step}: {e}")
        return False