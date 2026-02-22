import yfinance as yf
import pandas as pd
from datetime import datetime

def get_train_test_data(symbol="SPY", period="2y", train_ratio=0.8):
    """Real historical data for single asset."""
    data = yf.download(symbol, period=period, progress=False)['Close'].to_frame()
    split = int(len(data) * train_ratio)
    return data.iloc[:split], data.iloc[split:]

def get_multi_asset_data(symbols=None, period="2y"):
    """Real historical data for multiple assets (used by registry)."""
    if symbols is None:
        symbols = ["SPY", "QQQ", "IWM", "TLT", "GLD"]
    data = yf.download(symbols, period=period, progress=False)['Close']
    return data
