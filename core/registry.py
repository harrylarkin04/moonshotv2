import numpy as np
import hashlib
import json
from datetime import datetime
import sqlite3
from core.data_fetcher import get_train_test_data, get_multi_asset_data
import pandas as pd
import logging

# Initialize logger
logger = logging.getLogger('registry')
logger.setLevel(logging.INFO)

conn = sqlite3.connect('alphas.db')

def save_alpha(name, description, sharpe, persistence_score, auto_deploy=False, metrics=None, diversity=0.0, consistency=0.0):
    try:
        # ENHANCED: Stricter criteria for elite alphas
        if sharpe > 3.8 and persistence_score > 0.85:
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
            logger.info(f"Saved alpha: {name} | Sharpe: {sharpe:.2f} | Persistence: {persistence_score:.2f}")
            return True
        logger.warning(f"Alpha rejected: {name} | Sharpe: {sharpe:.2f} | Persistence: {persistence_score:.2f}")
        return False
    except Exception as e:
        logger.error(f"Save error: {e}")
        return False

def get_real_oos_metrics(strategy_fn):
    """Real walk-forward validation with historical data and volume-adjusted slippage"""
    try:
        full_data, _ = get_multi_asset_data(period="max")
        
        # Historical walk-forward split - FIXED: dynamic split date
        split_date = full_data.index[int(len(full_data)*0.7)]
        train = full_data.loc[:split_date]
        test = full_data.loc[split_date:]
        
        if test.empty:
            logger.warning("Test period empty in OOS validation")
            return {
                'sharpe': 0,
                'persistence': 0,
                'max_drawdown': 0,
                'period': 'N/A'
            }
        
        returns = []
        portfolio_value = 1.0
        peak_value = 1.0
        max_drawdown = 0.0
        
        # FIXED: Correct ADV calculation using volume data
        # IMPROVEMENT: Use actual volume data instead of mean price
        _, volume_data = get_multi_asset_data(period="max", include_volume=True)
        if volume_data is None:
            ADV = 1_000_000  # Fallback value
        else:
            test_volumes = volume_data.loc[split_date:]
            ADV = test_volumes.mean().mean()
        
        position = 0.0  # Track current position
        
        for i in range(1, len(test)):
            row = test.iloc[i]
            prev_row = test.iloc[i-1]
            
            asset_returns = (row / prev_row - 1).values
            signal = strategy_fn(prev_row)
            
            # Calculate target position
            target_position = signal * portfolio_value
            
            # Calculate trade size
            trade = target_position - position
            
            # ENHANCED: Volume-adjusted slippage model (5bp base + size impact)
            trade_size = abs(trade)
            slippage_bp = 5 + 20 * (trade_size / (0.1 * ADV)) ** 0.5
            slippage = slippage_bp / 10000 * trade_size
            
            # Update position
            position = target_position
            
            # Calculate return after slippage
            executed_return = np.dot(asset_returns, target_position) - slippage
            
            # Update portfolio metrics
            portfolio_value *= (1 + executed_return)
            peak_value = max(peak_value, portfolio_value)
            current_drawdown = (peak_value - portfolio_value) / peak_value
            max_drawdown = max(max_drawdown, current_drawdown)
            
            returns.append(executed_return)
        
        if len(returns) < 2:
            logger.warning("Insufficient returns for OOS validation")
            return {
                'sharpe': 0,
                'persistence': 0,
                'max_drawdown': 0,
                'period': f'{split_date.date()}_to_{test.index[-1].date()}'
            }
        
        returns = np.array(returns)
        ann_ret = np.mean(returns) * 252
        ann_vol = np.std(returns) * np.sqrt(252)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
        
        # FIXED: Correct persistence calculation (monthly basis)
        monthly_returns = pd.Series(returns, index=test.index[1:]).resample('M').apply(lambda x: (1+x).prod()-1)
        positive_months = (monthly_returns > 0).sum()
        persistence = positive_months / len(monthly_returns) if len(monthly_returns) > 0 else 0
        
        return {
            'sharpe': sharpe,
            'persistence': persistence,
            'max_drawdown': max_drawdown,
            'period': f'{split_date.date()}_to_{test.index[-1].date()}'
        }
    except Exception as e:
        logger.error(f"OOS validation failed: {str(e)}")
        return {
            'sharpe': 0,
            'persistence': 0,
            'max_drawdown': 0,
            'period': 'error'
        }
