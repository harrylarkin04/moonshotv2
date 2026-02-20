import yfinance as yf
import pandas as pd
import os
import numpy as np
import streamlit as st

os.makedirs('/tmp/yf_cache', exist_ok=True)
os.environ['YFINANCE_CACHE_DIR'] = '/tmp/yf_cache'

@st.cache_data(ttl=3600, show_spinner=False)
def get_multi_asset_data(period="2y"):
    tickers = ["SPY","QQQ","AAPL","MSFT","NVDA","TSLA","AMZN","GOOGL","META","IWM","GLD","TLT","BTC-USD"]
    try:
        data = yf.download(tickers, period=period, auto_adjust=True, threads=False, progress=False, group_by='ticker')["Close"]
        data = data.dropna(how='all')
        returns = data.pct_change().dropna()
        return data, returns
    except:
        # fallback synthetic (only used if yfinance fails)
        dates = pd.date_range(end=pd.Timestamp.today(), periods=1000)
        returns = pd.DataFrame(np.random.normal(0.0005, 0.012, (1000, len(tickers))), index=dates, columns=tickers)
        returns.iloc[0] = 0
        return (1 + returns).cumprod() * 100, returns

def get_train_test_data(train_ratio=0.72, period="300d"):
    """Strict split: In-Sample for evolution, Out-of-Sample for validation"""
    _, returns = get_multi_asset_data(period=period)
    split_idx = int(len(returns) * train_ratio)
    is_returns = returns.iloc[:split_idx]
    oos_returns = returns.iloc[split_idx:]
    return is_returns, oos_returns
