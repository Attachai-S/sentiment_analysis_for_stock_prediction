import pandas as pd
import re
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

USERTYPE = "personal" # or "university"
SYMBOLS = ["AAPL", "CSCO", "INTC", "MSFT", "NVDA", "ORCL"]
# SYMBOLS = ["AAPL"] # for testing
# SYMBOLS = ["MSFT", "NVDA", "ORCL"]

def selected_path(symbol, task="read", user_type="personal"):
    read_personal_path = f"news_collection/news_sentiment/sentiment_data/{symbol}_matching_fixed.csv"
    write_personal_path = f"news_collection/scored_data/{symbol}_scored.csv"
    #C:\Users\vangu\Desktop\CP465\news_collection\news_sentiment\sentiment_data\AAPL_matching_fixed.csv
    read_university_path = f"../news_collection/news_sentiment/sentiment_data/{symbol}_matching_fixed.csv"
    write_university_path = f"../news_collection/scored_data/{symbol}_scored.csv"
    if task == "read":
        if user_type == "personal":
            return read_personal_path
        elif user_type == "university":
            return read_university_path
    elif task == "write":
        if user_type == "personal":
            return write_personal_path
        elif user_type == "university":
            return write_university_path
    else:
        print(f"Invalid task: {task}")
        return None

def line(option="none", symbol=""):
    if option == "start": print(f"\n{"=" * 50}\n start score sentiment of {symbol} data \n{"=" * 50}\n")
    elif option == "end": print(f"\n{"=" * 50}\n end score sentiment of {symbol} data \n{"=" * 50}\n")
    else: print(f"\n{"=" * 50}\n")

def is_model_loaded(model_name):
    try:
        AutoTokenizer.from_pretrained(model_name, local_files_only=True)
        return True
    except Exception:
        return False

def load_model():
    global tokenizer, model
    MODEL_NAME = "ProsusAI/finbert"
    try:
        if is_model_loaded(MODEL_NAME):
            print("✅ model FinBERT downloaded previously, loading from local files...")
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, local_files_only=True)
        else:
            print("⏳ No model available, start downloading FinBERT, this may take a while...")
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            print(f"model {MODEL_NAME} downloaded and loaded successfully!")
        print("Model is ready to use!")
    except Exception as e:
        print(f"From def load_model: An error occurred while loading the model: {e}")


def sentiment_scoring(symbol):
    global tokenizer, model
    if tokenizer is None or model is None:
        print("Error: No model loaded. Please run load_model() first.")
        return
    try:
        _df = pd.read_csv(selected_path(symbol, "read", USERTYPE), encoding='utf-8')
        _clone_df = _df.copy()
        # _clone_df.info()
        labels, pos_scores, neg_scores, neu_scores = [], [], [], []
        for index, text in enumerate(_clone_df['model_text']):
            if pd.isna(text) or str(text).strip() == "" or str(text).strip() == "This news has no content":
                # ถ้าข่าวว่างเปล่า ให้คะแนนเป็น Neutral 100%
                labels.append("Neutral")
                pos_scores.append(0.0)
                neg_scores.append(0.0)
                neu_scores.append(1.0)
                continue
            
            inputs = tokenizer(str(text), return_tensors="pt", truncation=True, max_length=512)

            # โยนเข้าโมเดลเพื่อทำนาย (ไม่จำเป็นต้องจำ Gradient)
            with torch.no_grad():
                outputs = model(**inputs)

            # แปลงผลลัพธ์เป็นคะแนน 0-1
            probs = F.softmax(outputs.logits, dim=-1).squeeze().tolist()
            pos_score, neg_score, neu_score = probs[0], probs[1], probs[2]

            # หาคะแนนที่สูงที่สุดเพื่อติดป้าย (Label)
            max_index = probs.index(max(probs))
            label_map = {0: "Positive", 1: "Negative", 2: "Neutral"}
            
            labels.append(label_map[max_index])
            pos_scores.append(round(pos_score, 4))
            neg_scores.append(round(neg_score, 4))
            neu_scores.append(round(neu_score, 4))

            if (index + 1) % 100 == 0 or (index + 1) == len(_clone_df):
                print(f"Scoring {index + 1} / {len(_clone_df)} news items")

        # นำลิสต์คะแนนไปสร้างเป็นคอลัมน์ใหม่ใน DataFrame
        _clone_df['sentiment_label'] = labels
        _clone_df['positive_score'] = pos_scores
        _clone_df['negative_score'] = neg_scores
        _clone_df['neutral_score'] = neu_scores
        
        # if path not ex
        write_path = selected_path(symbol, "write", USERTYPE) 
        os.makedirs(os.path.dirname(write_path), exist_ok=True)
        
        # save to csv
        _clone_df.to_csv(selected_path(symbol, "write", USERTYPE), index=False, encoding='utf-8')
        print(f"Sentiment scoring for {symbol} completed and saved to {write_path}")

    except Exception as e:
        print(f"From def sentiment_scoring: An error occurred while processing {symbol}: {e}")


def pipeline() :
    load_model()
    for symbol in SYMBOLS:
        try :
            line("start", symbol)
            sentiment_scoring(symbol)
            line("end", symbol)
        except Exception as e:
             print(f"From def pipline: An error occurred while processing {symbol}: {e}")
             

pipeline()