import pandas as pd

SYMBOLS = ["AAPL", "CSCO", "INTC", "MSFT", "NVDA","ORCL"]

def clean_news_data():
    for symbol in SYMBOLS:
        try :
            news_df = pd.read_csv(f"news_dataset/news_{symbol}.csv")
            print(f"Hello, {symbol}!")
            news_df["cleaned_text"] = ""
            news_df.info()
            line()
        except FileNotFoundError:
            print(f"File for {symbol} not found. Skipping.")
            line()
        except Exception as e:
            print(f"An error occurred while processing {symbol}: {e}")
            line()


def line():
    print(f"\n","=" * 50,f"\n")

def single_clean():
    #read data
    news_df = pd.read_csv(r"news_collection\news_dataset\news_AAPL.csv")
    clone_df = news_df.copy() #copy for checking null values without affecting original data
    
    #check null values in summary column
    missing_in_column = clone_df['summary'].isnull()
    print(clone_df[missing_in_column]) #show rows with null values in summary column
    
    line()
    _null_mask = clone_df["summary"].isnull()
    _null_rows = clone_df[_null_mask]
    print(f"found summary null values: {len(_null_rows)}")

    #check null value indices
    if len(_null_rows) > 0:
        _null_arr = _null_rows.index.tolist()
        print(f"Null value indices: {_null_arr}")
    else:
        print("No null values found in the 'summary' column.")
    
    _empty_mask = (clone_df['summary'].notnull()) & (clone_df['summary'].astype(str).str.strip() == "")
    _empty_rows = clone_df[_empty_mask]

    if len(_empty_rows) > 0:
        _empty_arr = _empty_rows.index.tolist()
        print(f"Empty string value indices: {_empty_arr}")
    else:
        print("No empty string values found in the 'summary' column.")

    clone_df['summary'] = clone_df['summary'].fillna("No news content")
    clone_df['summary'] = clone_df['summary'].replace(r'^\s*$', "No news content", regex=True)

    #save data
    clone_df.to_csv(r"news_collection\news_processed\news_AAPL_cleaned.csv", index=False)
    
    # line()
    # news_df.info()

    #check specific row
    # line()
    # row_44 = news_df.loc[772]
    # print(row_44)

def check_data(num_loc):
    _df = pd.read_csv(r"news_collection\news_processed\news_AAPL_cleaned.csv")
    print(_df.iloc[num_loc])
    line()
    # _df.info()  
    empty_string_mask = _df['summary'].astype(str).str.strip() == ""
    empty_rows = _df[empty_string_mask]

    # 3. แสดงผลลัพธ์
    print(f"พบข้อมูลที่เป็น String ว่างเปล่า (\"\") จำนวน {len(empty_rows)} แถว")

    if len(empty_rows) > 0:
        empty_indices = empty_rows.index.tolist()
        print(f"เลขแถว (Row Index) ได้แก่: {empty_indices}")
        
        # แสดงตัวอย่างข้อมูล
        print("\n--- หน้าตาข้อมูลที่เป็น String ว่างเปล่า ---")
        print(empty_rows[['ticker', 'published_at', 'headline', 'summary']].head())

# clean_news_data()
single_clean()
check_data(151)
