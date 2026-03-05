# Use this file to run your code and test it
import requests
import pandas as pd
from datetime import date, timedelta
from news_collection.get_news_data import symbol, get_news

if __name__ == "__main__":
    API_KEY = ""  # Replace with your actual API key
    simbol = "AAPL"  # You can change this to any stock symbol you want
    get_news(symbol)