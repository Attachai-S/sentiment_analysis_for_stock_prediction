import pandas as pd
import re
import html
import os
# TASK = ["read", "write", "check", "sav_sentiment", "read_matching", "write_matching"]
# not nessary to use but can be used for checking data and cleaning data in the future if needed. (In this case we use own pc and university pc)
def selected_path(symbol,task="read", user_type="personal"):
    # personal path
    read_personal_path = f"news_collection/news_dataset/news_{symbol}.csv"
    write_personal_path = f"news_collection/news_processed/news_{symbol}_cleaned.csv"
    check_personal_path = f"news_collection/news_processed/news_{symbol}_cleaned.csv"
    sav_sentiment_personal_path = f"news_collection/news_sentiment/news_{symbol}_sentiment.csv"
    read_matching_personal_path = f"news_collection/news_sentiment/news_{symbol}_sentiment.csv"
    write_matching_personal_path = f"news_collection/news_sentiment/{symbol}_matching_fixed.csv"
    # university path
    read_university_path = f"../news_collection/news_dataset/news_{symbol}.csv"
    write_university_path = f"../news_collection/news_processed/news_{symbol}_cleaned.csv"
    check_university_path = f"../news_collection/news_processed/news_{symbol}_cleaned.csv"
    sav_sentiment_university_path = f"../news_collection/news_sentiment/news_{symbol}_sentiment.csv"
    read_matching_university_path = f"../news_collection/news_sentiment/news_{symbol}_sentiment.csv"
    write_matching_university_path = f"../news_collection/news_sentiment/{symbol}_matching_fixed.csv"
    try:
        if task == TASK[0]: # read
            if user_type == "personal":
                return read_personal_path
                # return personal_path
            elif user_type == "university":
                return read_university_path
        elif task == TASK[1]: # write
            if user_type == "personal":
                return write_personal_path
            elif user_type == "university":
                return write_university_path
        elif task == TASK[2]: # check
            if user_type == "personal":
                return check_personal_path
            elif user_type == "university":
                return check_university_path
        elif task == TASK[3]: #.sav_sentiment
            if user_type == "personal":
                return sav_sentiment_personal_path
            elif user_type == "university":
                return sav_sentiment_university_path
        elif task == TASK[4]: # read_matching
            if user_type == "personal":
                return read_matching_personal_path
            elif user_type == "university":
                return read_matching_university_path
        elif task == TASK[5]: # write_matching
            if user_type == "personal":
                return write_matching_personal_path
            elif user_type == "university":
                return write_matching_university_path
    except Exception as e:
        print(f"From def selected_path: An error occurred while determining the file path: {e}")
        return None

def line(option="none",symbol=""):
    if option == "start":
        print(f"\n","=" * 50,f"\n start clean {symbol} data \n","=" * 50,f"\n")
    elif option == "check":
        print(f"\n","=" * 50,f"\n Start check {symbol} data \n","=" * 50,f"\n")
    elif option == "end_check":
        print(f"\n","=" * 50,f"\n end check {symbol} data \n","=" * 50,f"\n")
    elif option == "mismatching":
        print(f"\n","=" * 50,f"\n Start checking encoding mismatch of {symbol} data \n","=" * 50,f"\n")
    else:
        print(f"\n","=" * 50,f"\n")
    

def check_data(symbol):
    _df = pd.read_csv(selected_path(symbol, TASK[2], USER_TYPE))
    line("check", symbol)
    empty_string_mask = _df['summary'].astype(str).str.strip() == ""
    empty_rows = _df[empty_string_mask]
    null_mask = _df['summary'].isnull()
    null_rows = _df[null_mask]
    print(f" Check and find empty String data (\"\")  {len(empty_rows)} row(s)")
    print(f" Check and find null values in 'summary' column: {len(null_rows)} row(s)")
    # Check empty string data indices (put in list and show spasific row(s))
    if len(empty_rows) > 0:
        empty_indices = empty_rows.index.tolist()
        print(f"Row Index : {empty_indices}")
        
        # show sample of row(s) of empty string data
        print("\n--- sample empty String data ---")
        print(empty_rows[['symbol', 'published_at', 'headline', 'summary']].head())
    line("end_check", symbol)

def fill_null(symbol):
    line("start",symbol)
    #read data
    news_df = pd.read_csv(selected_path(symbol, TASK[0], USER_TYPE))
    clone_df = news_df.copy() #copy for checking null values without affecting original data
    
    _null_mask = clone_df["summary"].isnull()
    _null_rows = clone_df[_null_mask]
    print(f"found summary null values: {len(_null_rows)}")

    #check null value indices
    if len(_null_rows) > 0:
        _null_arr = _null_rows.index.tolist()
        print(f"\nNull value indices: {_null_arr}")
    else:
        print("\nNo null values found in the 'summary' column.")
    
    _empty_str_mask = (clone_df['summary'].notnull()) & (clone_df['summary'].astype(str).str.strip() == "")
    _empty_str_rows = clone_df[_empty_str_mask]
    print(f"\nfound empty string data values: {len(_empty_str_rows)}")

    if len(_empty_str_rows) > 0:
        _empty_str_arr = _empty_str_rows.index.tolist()
        print(f"\nEmpty string value (Not Null) indices: {_empty_str_arr}")
    else:
        print("\nNo empty string values found in the 'summary' column.")

    clone_df['summary'] = clone_df['summary'].fillna("No content of news")
    clone_df['summary'] = clone_df['summary'].replace(r'^\s*$', "No content of news", regex=True)
    print(f"\nAll Null data on \"{symbol}\" fixed")
    #save data
    clone_df.to_csv(selected_path(symbol, TASK[1], USER_TYPE), index=False),print(f"\nSaved cleaned data of \"{symbol}\" to csv file")

def prepare_final_data(symbol):
    def cleansing_noise(text):
        if pd.isna(text) or text in ["No news content", "No content of news", "nan"]:
            return ""
        text = str(text)

        text = html.unescape(text)# change HTML format to normal character (ex &#39; to ')
        text = re.sub(r'http[s]?://\S+|www\.\S+', '', text)# delete all url ..
        text = re.sub(r'(?i)click.*$', '', text) # delete all after "click" word
        text = re.sub(r'(?i)read.*$', '', text) # delete all after "read" word
        text = re.sub(r'(?i)Check out why.*$', '', text) # delete all after "Check out why" word
        text = re.sub(r'(?i)Read why I.*$', '', text) # delete all after "Read why I" word
        text = text.replace('\xa0', ' ') # delete all space character
        text = re.sub(r'\s{2,}', ' ', text).strip() # delete multiple space to 1 space      
        text = re.sub(r'(?i)DO NOT DELETE - 404 Page', 'This news has no content', text) # Change this "DO NOT DELETE - 404 Page" to "This news has no content"
        text = re.sub(r'\.\.+', '.', text) # replace .. with . where ever in line  

        return text
    try:
        _df = pd.read_csv(selected_path(symbol, TASK[1], USER_TYPE))
        _clone_df = _df.copy() #copy for checking null values without affecting original data
        print(f"\nStart cleansing noise data of \"{symbol}\" ...")
        _clone_df['headline_clean'] = _clone_df['headline'].apply(cleansing_noise)
        _clone_df['summary_clean'] = _clone_df['summary'].apply(cleansing_noise)
        _clone_df['model_text'] = _clone_df.apply(
            
            lambda row: f"{row['headline_clean']} {row['summary_clean']}"
            if row['summary_clean'] != "" else row['headline_clean'],
            axis=1
        )
        _clone_df['model_text'] = _clone_df['model_text'].apply(lambda x: x.replace('..', '.'))
        _clone_df = _clone_df[["ticker", "published_at", "model_text"]]
        _clone_df.to_csv(selected_path(symbol, TASK[3], USER_TYPE), index=False)
        print(f"Finished cleansing noise data of \"{symbol}\" and saved to csv file")
    except FileNotFoundError:
        print(f"From def prepare_final_data: File for {symbol} not found. Skipping.")
    except Exception as e:
        print(f"An error occurred while preparing final data for {symbol}: {e}")

def  Encoding_Mismatch():
    try : 
        for symbol in SYMBOLS:
            line("mismatching", symbol)
            _df = pd.read_csv(selected_path(symbol, TASK[4], USER_TYPE))
            _clone_df = _df.copy()
            _clone_df.to_csv(selected_path(symbol, TASK[5], USER_TYPE), index=False)
    except FileNotFoundError:
        print(f"From  def Encoding_Mismatch: File not found during encoding check: {symbol}. Skipping.")
    except Exception as e:
        print(f"from def Encoding_Mismatch: An error occurred while checking encoding mismatch: {e}")


def clean_news_data():
    for symbol in SYMBOLS:
        try :
            fill_null(symbol)
            check_data(symbol)
            prepare_final_data(symbol)
            Encoding_Mismatch()
        except FileNotFoundError:
            print(f"From def clean_news_data: File for {symbol} not found. Skipping.")
            line()
        except Exception as e:
            print(f"From def clean_news_data: An error occurred while processing {symbol}: {e}")
            line()

SYMBOLS = ["AAPL", "CSCO", "INTC", "MSFT", "NVDA","ORCL"]
USER_TYPE = "personal" # or "university" 
TASK = ["read", "write", "check", "sav_sentiment", "read_matching", "write_matching"]
clean_news_data()