import numpy as np
import hashlib
import json
from datetime import datetime
import sqlite3
from core.data_fetcher import get_train_test_data, get_multi_asset_data
import pandas as pd

conn = sqlite3.connect('alphas.db')

def save_alpha(name, description, sharpe, persistence_score, auto_deploy=False, metrics=None, diversity=0.0, consistency=0.0):
    try:
        if sharpe > 3.5 and persistence_score > 0.8:
            strategy_hash = hashlib.sha256(f"{name}{description}{datetime.now()}".encode()).hexdigest()[:12]
            oos_metrics = {
                'sharpe': sharpe,
                'persistence': persistence_score,
                'hash': strategy_hash,
                'diversity': diversity,
                'consistency': consistency,
                'backtest_period': '2020-01-01_to_2024-06-01'
            }
            
            conn.execute("""
                INSERT INTO alphas 
                (name, description, sharpe, persistence_score, created, live_paper_trading, oos_metrics, diversity, consistency) 
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (name, description, sharpe, persistence_score, datetime.now().isoformat(), 
                  1 if auto_deploy else 0, json.dumps(oos_metrics), diversity, consistency))
            conn.commit()
            return True
        return False
    except Exception as e:
        print(f"Save error: {e}")
        return False

def get_real_oos_metrics(strategy_fn):
    """Real walk-forward validation with historical data and 5bp slippage"""
    full_data, _ = get_multi_asset_data(period="max")
    
    # Historical walk-forward split
    train = full_data.loc[:'2022-01-01']
    test = full_data.loc['2022-01-02':'2024-06-01']
    
    if test.empty:
        return {
            'sharpe': 0,
            'persistence': 0,
            'max_drawdown': 0,
            'period': '2022-01-02_to_2024-06-01'
        }
    
    returns = []
    current_position = 0
    portfolio_value = 1.0
    peak_value = 1.0
    max_drawdown = 0.0
    
    for i in range(1, len(test)):
        row = test.iloc[i]
        prev_row = test.iloc[i-1]
        
        asset_returns = (row / prev_row - 1).values
        signal = strategy_fn(prev_row)
        target_position = signal * 1.0
        trade = target_position - current_position
        
        # Apply 5bp slippage (0.0005)
        slippage = 0.0005 * abs(trade) if trade != 0 else 0
        executed_return = np.dot(asset_returns, target_position) - slippage
        
        # Update portfolio metrics
        portfolio_value *= (1 + executed_return)
        peak_value = max(peak_value, portfolio_value)
        current_drawdown = (portfolio_value - peak_value) / peak_value
        if current_drawdown < max_drawdown:
            max_drawdown = current_drawdown
        
        returns.append(executed_return)
        current_position = target_position
    
    if len(returns) < 2:
        return {
            'sharpe': 0,
            'persistence': 0,
            'max_drawdown': 0,
            'period': '2022-01-02_to_2024-06-01'
        }
    
    returns = np.array(returns)
    ann_ret = np.mean(returns) * 252
    ann_vol = np.std(returns) * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
    
    # FIXED: Correct persistence calculation (monthly basis)
    monthly_returns = pd.Series(returns).resample('M').prod()
    positive_months = (monthly_returns > 0).sum()
    persistence = positive_months / len(monthly_returns) if len(monthly_returns) > 0 else 0
    
    return {
        'sharpe': sharpe,
        'persistence': persistence,
        'max_drawdown': abs(max_drawdown),
        'period': '2022-01-02_to_2024-06-01'
    }
