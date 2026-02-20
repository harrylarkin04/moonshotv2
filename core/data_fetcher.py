import yfinance as yf
import pandas as pd

def get_multi_asset_data(period="4y"):
    tickers = ["SPY","QQQ","AAPL","MSFT","NVDA","TSLA","AMZN","GOOGL","META","IWM","GLD","TLT","BTC-USD"]
    data = yf.download(tickers, period=period, auto_adjust=True)["Close"].dropna(how='all')
    returns = data.pct_change().dropna()
    return data, returns
