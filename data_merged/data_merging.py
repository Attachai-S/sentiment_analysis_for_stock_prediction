import numpy as np
import pandas as pd

# SYMBOLS = ['AAPL'] #For testing
SYMBOLS = ["AAPL", "CSCO", "INTC", "MSFT", "NVDA","ORCL"]
USERTYPE = "personal" # or "university"
def selected_path(symbol, user_type, task):
    read_stock = f"stock_collection/stock_dataset/stock_{symbol}.csv"
    read_sentiment = f"news_collection/scored_data/{symbol}_scored.csv"
    save_merged = f"data_merged/merged_{symbol}.csv"
    
    if task == "read_stock": return read_stock
    elif task == "read_sentiment": return read_sentiment
    elif task == "save_merged": return save_merged

def line(symbol, task=""):
    if task == "start": print(f"\n{'=' * 50}\n start on {symbol} \n{'=' * 50}\n")
    elif task == "end": print(f"\n{'=' * 50}\n end on {symbol} \n{'=' * 50}\n")
    else: print(f"\n{'=' * 50}\n")

def change_date_format(symbol):
    _stock = pd.read_csv(selected_path(symbol, USERTYPE, "read_stock")) #readed
    _sentiment = pd.read_csv(selected_path(symbol, USERTYPE, "read_sentiment")) #readed

    _stock['Date'] = pd.to_datetime(_stock['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
    _stock = _stock.dropna(subset=['Date'])

    _sentiment['Date'] = pd.to_datetime(_sentiment['published_at'], errors='coerce').dt.strftime('%Y-%m-%d')
    _sentiment = _sentiment.dropna(subset=['Date'])
    
    return _stock, _sentiment

def data_merging(symbol):
    # 1. รับข้อมูลที่แก้ไขวันที่แล้วมาจาก change_date_format
    df_stock, df_sent = change_date_format(symbol)
    print(f"finish change date format for {symbol}")
    # 2. สรุปข้อมูลข่าวในแต่ละวัน (Daily Aggregation)
    # หาค่าเฉลี่ยคะแนน
    daily_scores = df_sent.groupby('Date')[['positive_score', 'negative_score', 'neutral_score']].mean()
    # นับจำนวนข่าว
    daily_counts = df_sent.groupby('Date').size().rename('news_count')
    
    # หาอารมณ์หลักของวัน (Label)
    daily_scores['sentiment_label'] = daily_scores[['positive_score', 'negative_score', 'neutral_score']].idxmax(axis=1)
    daily_scores['sentiment_label'] = daily_scores['sentiment_label'].map({
        'positive_score': 'Positive',
        'negative_score': 'Negative',
        'neutral_score': 'Neutral'
    })
    
    daily_sentiment = pd.concat([daily_scores, daily_counts], axis=1).reset_index()
    
    # 3. นำตารางข่าวมาแปะติดกับตารางหุ้น (Left Join)
    merged_df = pd.merge(df_stock, daily_sentiment, on='Date', how='left')
    
    # 4. จัดการค่าว่าง (วันที่หุ้นเปิด แต่ไม่มีข่าว)
    merged_df['news_count'] = merged_df['news_count'].fillna(0).astype(int)
    merged_df['positive_score'] = merged_df['positive_score'].fillna(0.0).round(4)
    merged_df['negative_score'] = merged_df['negative_score'].fillna(0.0).round(4)
    merged_df['neutral_score'] = merged_df['neutral_score'].fillna(1.0).round(4)
    merged_df['sentiment_label'] = merged_df['sentiment_label'].fillna('Neutral')
    
    # 5. จัดเรียงคอลัมน์ตามที่ระบุ
    final_columns = [
        'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 
        'news_count', 'positive_score', 'negative_score', 'neutral_score', 'sentiment_label'
    ]
    merged_df = merged_df[final_columns]
    
    # 6. บันทึกไฟล์

    merged_df.to_csv(selected_path(symbol, USERTYPE, "save_merged"), index=False, encoding='utf-8')
    print(f"finish merged data for {symbol} ")


def price_movement_labeling(symbol):
    _df = pd.read_csv(selected_path(symbol, USERTYPE, "save_merged"), encoding='utf-8')
    _clone_df = _df.copy()
    yesterday_close = _clone_df['Close'].shift(1)
    conditions = [
        (_clone_df['Close'] > yesterday_close), # ราคาขึ้น
        (_clone_df['Close'] < yesterday_close), # ราคาลง
        (_clone_df['Close'] == yesterday_close) # ราคาเท่าเดิม
    ]
    choices = ['up', 'down', 'stable']
    # 3. ใส่ Label โดยใช้ np.select (ถ้าเทียบไม่ได้ เช่น แถวแรก จะได้ค่าเริ่มต้นเป็น stable)
    _clone_df['price_movement'] = np.select(conditions, choices, default='stable')
    
    # 4. บันทึกไฟล์ผลลัพธ์สุดท้าย
    save_path = selected_path(symbol, USERTYPE, "save_merged")
    _clone_df.to_csv(save_path, index=False, encoding='utf-8')
    
    print(f"finish price movement labeling for {symbol}")

def data_merger():
    for symbol in SYMBOLS:
        line(symbol, task="start")
        change_date_format(symbol)
        data_merging(symbol)
        price_movement_labeling(symbol)
        line(symbol, task="end")
if __name__ == "__main__":
    data_merger()

def auto_pipline_data_merger(symbol):
    change_date_format(symbol)
    data_merging(symbol)
    price_movement_labeling(symbol)
    return True