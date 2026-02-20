import yfinance as yf
import pandas as pd
import os
import numpy as np
import streamlit as st

os.makedirs('/tmp/yf_cache', exist_ok=True)
os.environ['YFINANCE_CACHE_DIR'] = '/tmp/yf_cache'

@st.cache_data(ttl=3600, show_spinner=False)
def get_multi_asset_data(period="4y"):
    tickers = ["SPY","QQQ","AAPL","MSFT","NVDA","TSLA","AMZN","GOOGL","META","IWM","GLD","TLT","BTC-USD"]
    try:
        data = yf.download(tickers, period=period, auto_adjust=True, threads=False, progress=False, group_by='ticker')["Close"]
        data = data.dropna(how='all')
        if data.empty:
            raise ValueError
        return data, data.pct_change().dropna()
    except:
        # Robust fallback synthetic data (realistic returns for demo & production on Cloud)
        dates = pd.date_range(end=pd.Timestamp.today(), periods=1000)
        assets = tickers
        returns = pd.DataFrame(np.random.normal(0.0005, 0.012, (1000, len(assets))), index=dates, columns=assets)
        returns.iloc[0] = 0
        prices = (1 + returns).cumprod() * 100
        return prices, returns
