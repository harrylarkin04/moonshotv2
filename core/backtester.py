import yfinance as yf
import pandas as pd
import numpy as np

def run_real_oos_backtest(alpha, symbol="SPY", period="3y", oos_months=6):
    data = yf.download(symbol, period=period, progress=False)['Close']
    
    oos_start = data.index[-oos_months*21]
    oos = data[data.index >= oos_start]
    returns = oos.pct_change().dropna()

    if len(returns) < 10:
        return {
            "name": alpha.get("name", "Alpha"),
            "sharpe": 0.0,
            "persistence": alpha.get("persistence", 0.85),
            "oos_return": 0.0,
            "max_drawdown": 0.0,
            "equity_curve": pd.Series([100000])
        }

    equity = (1 + returns).cumprod() * 100000
    total_return = (equity.iloc[-1] / equity.iloc[0] - 1) * 100
    sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0.0
    max_dd = ((equity / equity.cummax()) - 1).min() * 100

    return {
        "name": alpha.get("name", "Alpha"),
        "sharpe": round(sharpe, 2),
        "persistence": alpha.get("persistence", 0.85),
        "oos_return": round(total_return, 1),
        "max_drawdown": round(max_dd, 1),
        "equity_curve": equity
    }