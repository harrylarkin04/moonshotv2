import yfinance as yf
import pandas as pd
import numpy as np

def get_multi_asset_data(period="max", include_volume=False):
    """Fetch real multi-asset data using yfinance"""
    tickers = ['SPY', 'QQQ', 'TLT', 'GLD']  # Example tickers
    data = yf.download(tickers, period=period)
    
    # ENHANCED: Return volume data if requested
    if include_volume:
        volumes = data['Volume'] if 'Volume' in data.columns else None
        adj_close = data['Adj Close']
        returns = adj_close.pct_change().dropna()
        return adj_close, returns, volumes
    else:
        adj_close = data['Adj Close']
        returns = adj_close.pct_change().dropna()
        return adj_close, returns
