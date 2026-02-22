import yfinance as yf
import pandas as pd

def get_train_test_data(symbol="SPY", period="2y", train_ratio=0.8):
    data = yf.download(symbol, period=period, progress=False)['Close'].to_frame()
    split = int(len(data) * train_ratio)
    return data.iloc[:split], data.iloc[split:]
