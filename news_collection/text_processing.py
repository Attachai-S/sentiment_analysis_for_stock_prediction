import pandas as pd

SYMBOLS = ["AAPL", "CSCO", "INTC", "MSFT", "NVDA","ORCL"]

def line(option="none",ticker=""):
    if option == "start":
        print(f"\n","=" * 50,f"\n start clean {ticker} data \n","=" * 50,f"\n")
    elif option == "check":
        print(f"\n","=" * 50,f"\n Start check {ticker} data \n","=" * 50,f"\n")
    elif option == "end_check":
        print(f"\n","=" * 50,f"\n end check {ticker} data \n","=" * 50,f"\n")
    else:
        print(f"\n","=" * 50,f"\n")

def check_data(ticker):
    _df = pd.read_csv(f"news_collection/news_processed/news_{ticker}_cleaned.csv")
    
    line("check", ticker)
    empty_string_mask = _df['summary'].astype(str).str.strip() == ""
    empty_rows = _df[empty_string_mask]
    null_mask = _df['summary'].isnull()
    null_rows = _df[null_mask]
    print(f" Check and find empty String data (\"\")  {len(empty_rows)} row(s)")
    print(f" Check and find null values in 'summary' column: {len(null_rows)} row(s)")

    if len(empty_rows) > 0:
        empty_indices = empty_rows.index.tolist()
        print(f"Row Index : {empty_indices}")
        
        # แสดงตัวอย่างข้อมูล
        print("\n--- sample empty String data ---")
        print(empty_rows[['ticker', 'published_at', 'headline', 'summary']].head())
    line("end_check", ticker)

def fill_null(ticker):
    #read data
    line("start",ticker)
    news_df = pd.read_csv(f"news_collection/news_dataset/news_{ticker}.csv")
    clone_df = news_df.copy() #copy for checking null values without affecting original data
    
    #check null values in summary column
    missing_in_column = clone_df['summary'].isnull()
    print(f"---missing data row(s)---")
    
    line()
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
    print(f"\nAll Null data on \"{ticker}\" fixed")
    #save data
    clone_df.to_csv(f"news_collection/news_processed/news_{ticker}_cleaned.csv", index=False)

def spacial_characters_handled(symbol):
    # Implementation for handling special characters
    pass

def clean_news_data():
    for symbol in SYMBOLS:
        try :
            fill_null(symbol)
            spacial_characters_handled(symbol)
            check_data(symbol)
        except FileNotFoundError:
            print(f"File for {symbol} not found. Skipping.")
            line()
        except Exception as e:
            print(f"An error occurred while processing {symbol}: {e}")
            line()

clean_news_data()