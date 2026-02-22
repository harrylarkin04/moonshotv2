import yfinance as yf
import pandas as pd
import numpy as np
import logging

# Initialize logger
logger = logging.getLogger('data_fetcher')
logger.setLevel(logging.INFO)

def get_multi_asset_data(period="max", include_volume=False):
    """Fetch real multi-asset data using yfinance"""
    try:
        tickers = ['SPY', 'QQQ', 'TLT', 'GLD', 'VXX', 'USO', 'TLT', 'IWM']  # More diverse assets
        data = yf.download(tickers, period=period, group_by='ticker')
        
        # ENHANCED: Return volume data if requested
        if include_volume:
            volumes = pd.DataFrame()
            adj_close = pd.DataFrame()
            
            for t in tickers:
                if t in data:
                    adj_close[t] = data[t]['Adj Close']
                    volumes[t] = data[t]['Volume']
            
            returns = adj_close.pct_change().dropna()
            return adj_close, returns, volumes
        else:
            adj_close = pd.DataFrame()
            for t in tickers:
                if t in data:
                    adj_close[t] = data[t]['Adj Close']
            
            returns = adj_close.pct_change().dropna()
            return adj_close, returns
    except Exception as e:
        logger.error(f"Data fetch failed: {str(e)}")
        # Return empty DataFrames with expected structure
        if include_volume:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        return pd.DataFrame(), pd.DataFrame()
