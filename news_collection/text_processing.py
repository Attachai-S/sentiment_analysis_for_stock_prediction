import pandas as pd
import re
import html

SYMBOLS = ["AAPL", "CSCO", "INTC", "MSFT", "NVDA", "ORCL"]
USER_TYPE = "personal" # or "university" 
TASK = ["read", "write", "check", "sav_sentiment", "read_matching", "write_matching"]

def selected_path(symbol, task="read", user_type="personal"):
    # personal path
    read_personal_path = f"news_collection/news_dataset/news_{symbol}.csv"
    write_personal_path = f"news_collection/news_processed/news_{symbol}_cleaned.csv"
    check_personal_path = f"news_collection/news_processed/news_{symbol}_cleaned.csv"
    sav_sentiment_personal_path = f"news_collection/news_sentiment/news_{symbol}_sentiment.csv"
    read_matching_personal_path = f"news_collection/news_sentiment/news_{symbol}_sentiment.csv"
    write_matching_personal_path = f"news_collection/news_sentiment/sentiment_data/{symbol}_matching_fixed.csv"
    # university path
    read_university_path = f"../news_collection/news_dataset/news_{symbol}.csv"
    write_university_path = f"../news_collection/news_processed/news_{symbol}_cleaned.csv"
    check_university_path = f"../news_collection/news_processed/news_{symbol}_cleaned.csv"
    sav_sentiment_university_path = f"../news_collection/news_sentiment/news_{symbol}_sentiment.csv"
    read_matching_university_path = f"../news_collection/news_sentiment/news_{symbol}_sentiment.csv"
    write_matching_university_path = f"../news_collection/news_sentiment/sentiment_data/{symbol}_matching_fixed.csv"
    
    try:
        if task == TASK[0]: return read_personal_path if user_type == "personal" else read_university_path
        elif task == TASK[1]: return write_personal_path if user_type == "personal" else write_university_path
        elif task == TASK[2]: return check_personal_path if user_type == "personal" else check_university_path
        elif task == TASK[3]: return sav_sentiment_personal_path if user_type == "personal" else sav_sentiment_university_path
        elif task == TASK[4]: return read_matching_personal_path if user_type == "personal" else read_matching_university_path
        elif task == TASK[5]: return write_matching_personal_path if user_type == "personal" else write_matching_university_path
    except Exception as e:
        print(f"From def selected_path: An error occurred while determining the file path: {e}")
        return None
    
def line(option="none", symbol=""):
    if option == "start": print(f"\n{"=" * 50}\n start clean {symbol} data \n{"=" * 50}\n")
    elif option == "start_check": print(f"\n{"=" * 50}\n Start check {symbol} data \n{"=" * 50}\n")
    elif option == "end_check": print(f"\n{"=" * 50}\n end check {symbol} data \n{"=" * 50}\n")
    elif option == "start_cleansing": print(f"\n{"=" * 50}\n start cleansing {symbol} data \n{"=" * 50}\n")
    elif option == "end_cleansing": print(f"\n{"=" * 50}\n end cleansing {symbol} data \n{"=" * 50}\n")
    elif option == "start_mismatching": print(f"\n{"=" * 50}\n Start checking encoding mismatch of {symbol} data \n{"=" * 50}\n")
    elif option == "end_mismatching": print(f"\n{"=" * 50}\n end checking encoding mismatch of {symbol} data \n{"=" * 50}\n")
    else: print(f"\n{"=" * 50}\n")

def fill_null(symbol):
    line("start", symbol)
    news_df = pd.read_csv(selected_path(symbol, TASK[0], USER_TYPE), encoding='utf-8')
    _clone_df = news_df.copy()
    
    _null_mask = _clone_df["summary"].isnull()
    _null_rows = _clone_df[_null_mask]
    print(f"found summary null values: {len(_null_rows)}")

    _empty_str_mask = (_clone_df['summary'].notnull()) & (_clone_df['summary'].astype(str).str.strip() == "")
    _empty_str_rows = _clone_df[_empty_str_mask]
    print(f"found empty string data values: {len(_empty_str_rows)}")

    _clone_df['summary'] = _clone_df['summary'].fillna("No content of news")
    _clone_df['summary'] = _clone_df['summary'].replace(r'^\s*$', "No content of news", regex=True)
    print(f"All Null data on \"{symbol}\" fixed")
    
    # sav file
    _clone_df.to_csv(selected_path(symbol, TASK[1], USER_TYPE), index=False, encoding='utf-8')
    print(f"Saved cleaned data of \"{symbol}\" to csv file")

def cleansing_noise_text(symbol): # clear noise in headline and summary, then combine them to new column "model_text"
    def cleansing_noise(text):
        if pd.isna(text) or text in ["No news content", "No content of news", "nan"]:
            return ""
        text = str(text)
        text = html.unescape(text)
        text = re.sub(r'http[s]?://\S+|www\.\S+', '', text)
        text = re.sub(r'(?i)click here.*$', '', text)
        text = re.sub(r'(?i)read more.*$', '', text)
        text = re.sub(r'(?i)Check out why.*$', '', text)
        text = re.sub(r'(?i)Read why I.*$', '', text)
        text = text.replace('\xa0', ' ')
        text = re.sub(r'\s{2,}', ' ', text).strip()      
        text = re.sub(r'(?i)DO NOT DELETE - 404 Page', 'This news has no content', text)
        text = re.sub(r'\.\.+', '.', text)
        return text
    
    try:
        # sav file
        _df = pd.read_csv(selected_path(symbol, TASK[1], USER_TYPE), encoding='utf-8')
        _clone_df = _df.copy() 
        
        _clone_df['headline_clean'] = _clone_df['headline'].apply(cleansing_noise)
        _clone_df['summary_clean'] = _clone_df['summary'].apply(cleansing_noise)
        _clone_df['model_text'] = _clone_df.apply(
            lambda row: f"{row['headline_clean']} {row['summary_clean']}"
            if row['summary_clean'] != "" else row['headline_clean'],
            axis=1
        )
        _clone_df['model_text'] = _clone_df['model_text'].apply(lambda x: x.replace('..', '.'))
        _clone_df = _clone_df[["ticker", "published_at", "model_text"]]
        
        # sav file
        _clone_df.to_csv(selected_path(symbol, TASK[3], USER_TYPE), index=False, encoding='utf-8')
        print(f"Finished cleansing noise data of \"{symbol}\" and saved to csv file")
    except Exception as e:
        print(f"From def prepare_final_data: An error occurred while preparing final data for {symbol}: {e}")

def encoding_mismatch(symbol):
    try : 
        line("start_mismatching", symbol)
        # sav file
        _df = pd.read_csv(selected_path(symbol, TASK[4], USER_TYPE), encoding='utf-8')
        _clone_df = _df.copy()

        mojibake_dict = {
            "Ã¢Â€Â™": "'", "â€™": "'", "â€œ": '"', "â€": '"', "â€”": "-", 
            "â€“": "-", "â€˜": "'", "â€¦": "...", "â€": '"', "Â": " ",
            "’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-", "…": "...",
            "\u200c": "", "\u200b": "", "\u2060": "", "\u200d": "",
            "®": "", "™": "", "©": "", "↘️": "", "↗️": "", "‑": "-"
        }
        
        def fix_text(text): 
            if pd.isna(text): return text
            text = str(text)
            for broken_char, fixed_char in mojibake_dict.items():
                if broken_char in text:
                    text = text.replace(broken_char, fixed_char)
            return text
            
        if 'model_text' in _clone_df.columns:
            pattern = '|'.join(map(re.escape, mojibake_dict.keys()))
            _mismatch_mask = _clone_df['model_text'].str.contains(pattern, regex=True, na=False)
            _changed_indices = _clone_df[_mismatch_mask].index.tolist()
            
            print(f"Found and fixing Mojibake / Smart Quotes in {len(_changed_indices)} rows.")
            _clone_df['model_text'] = _clone_df['model_text'].apply(fix_text) 
        
        # sav file
        _clone_df.to_csv(selected_path(symbol, TASK[5], USER_TYPE), index=False, encoding='utf-8')
        
        print(f"Finished checking encoding mismatch of \"{symbol}\" and saved to csv file")
        line("end_mismatching", symbol)
        
    except Exception as e:
        print(f"from def Encoding_Mismatch: An error occurred while checking encoding mismatch: {e}")

def prepare_final_data(symbol):
    pass

def pipline():
    for symbol in SYMBOLS:
        try :
            fill_null(symbol)
            cleansing_noise_text(symbol)
            encoding_mismatch(symbol)
            prepare_final_data(symbol)
        except Exception as e:
            print(f"From def pipline: An error occurred while processing {symbol}: {e}")
            line()

pipline()