def get_stock_data(symbol):
    pass

def selected_path(symbol, user_type):
    if user_type == "personal":
        sav_stock_data_personal = f"stock_collection/stock_dataset/stock_{symbol}.csv"
        return sav_stock_data_personal
    elif user_type == "university":
        sav_stock_data_university = f"../stock_collection/stock_dataset/stock_{symbol}.csv"
        return sav_stock_data_university

SYMBOLS = ["AAPL", "CSCO", "INTC", "MSFT", "NVDA","ORCL"]
USER_TYPE = "personal" # or "university"

def start_get_stock_data(symbol):
    try:
        get_stock_data(symbol)
    except Exception as e:
        print(f"From start_get_stock_data: An error occurred while fetching stock data for {symbol}: {e}")

