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
        tickers = ['SPY', 'QQQ', 'TLT', 'GLD', 'VXX', 'USO', 'IWM', 'EEM']  # More diverse assets
        data = yf.download(tickers, period=period, group_by='ticker', threads=True)
        
        # ENHANCED: Handle missing tickers and return volume data
        adj_close = pd.DataFrame()
        volumes = pd.DataFrame()
        
        for t in tickers:
            if t in data:
                if not data[t]['Adj Close'].empty:
                    adj_close[t] = data[t]['Adj Close']
                if include_volume and not data[t]['Volume'].empty:
                    volumes[t] = data[t]['Volume']
        
        if adj_close.empty:
            logger.warning("No valid assets found")
            if include_volume:
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            return pd.DataFrame(), pd.DataFrame()
        
        returns = adj_close.pct_change().dropna()
        
        if include_volume:
            return adj_close, returns, volumes
        return adj_close, returns
    except Exception as e:
        logger.error(f"Data fetch failed: {str(e)}")
        if include_volume:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        return pd.DataFrame(), pd.DataFrame()
