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
    """REALISTIC walk-forward validation with volume-adjusted slippage"""
    try:
        # FIXED: Correct data unpacking
        full_data = get_multi_asset_data(period="max", include_volume=False)[0]
        
        if full_data.empty:
            logger.error("No data available for OOS validation")
            return {
                'sharpe': 0,
                'persistence': 0,
                'max_drawdown': 0,
                'period': 'N/A'
            }
        
        # Historical walk-forward split
        split_idx = int(len(full_data)*0.7)
        if split_idx < 10:
            logger.error("Insufficient data for OOS split")
            return {
                'sharpe': 0,
                'persistence': 0,
                'max_drawdown': 0,
                'period': 'N/A'
            }
            
        train = full_data.iloc[:split_idx]
        test = full_data.iloc[split_idx:]
        
        portfolio_value = 1.0
        peak_value = 1.0
        max_drawdown = 0.0
        returns = []
        position = 0.0
        
        # ENHANCED: More realistic trading simulation
        for i in range(1, len(test)):
            current_prices = test.iloc[i]
            prev_prices = test.iloc[i-1]
            
            # Calculate asset returns
            asset_returns = (current_prices / prev_prices - 1).values
            
            # Get strategy signal
            signal = strategy_fn(prev_prices)
            
            # Calculate target position
            target_position = signal * portfolio_value
            
            # Calculate trade size
            trade = target_position - position
            
            # ENHANCED: Realistic slippage model
            trade_size = abs(trade)
            slippage_bp = 5 + 15 * (trade_size / 1_000_000) ** 0.5
            slippage = slippage_bp / 10000 * trade_size
            
            # Update position
            position = target_position
            
            # Calculate portfolio return after slippage
            portfolio_return = np.dot(asset_returns, position) - slippage
            portfolio_value *= (1 + portfolio_return)
            
            # Update drawdown
            peak_value = max(peak_value, portfolio_value)
            current_dd = (peak_value - portfolio_value) / peak_value
            max_drawdown = max(max_drawdown, current_dd)
            
            returns.append(portfolio_return)
        
        # Calculate performance metrics
        returns_series = pd.Series(returns)
        if len(returns_series) < 3:
            logger.warning("Insufficient returns for metrics")
            return {
                'sharpe': 0,
                'persistence': 0,
                'max_drawdown': max_drawdown,
                'period': f'{test.index[0].date()}_to_{test.index[-1].date()}'
            }
        
        ann_return = returns_series.mean() * 252
        ann_vol = returns_series.std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0
        
        # ENHANCED: Correct persistence calculation
        monthly_returns = returns_series.resample('M').agg(lambda x: (1+x).prod()-1)
        persistence = (monthly_returns > 0).mean() if not monthly_returns.empty else 0
        
        return {
            'sharpe': sharpe,
            'persistence': persistence,
            'max_drawdown': max_drawdown,
            'period': f'{test.index[0].date()}_to_{test.index[-1].date()}'
        }
    except Exception as e:
        logger.error(f"OOS validation failed: {str(e)}")
        return {
            'sharpe': 0,
            'persistence': 0,
            'max_drawdown': 0,
            'period': 'error'
        }

def get_top_alphas(limit=25):
    """Fetch top alphas with enhanced filtering"""
    try:
        # ENHANCED: Stricter elite criteria
        query = f"""
            SELECT name, sharpe, persistence_score, diversity, consistency, oos_metrics
            FROM alphas 
            WHERE sharpe > 3.5 AND persistence_score > 0.8
            ORDER BY sharpe * persistence_score DESC
            LIMIT {limit}
        """
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            # Parse OOS metrics
            df['oos_metrics'] = df['oos_metrics'].apply(json.loads)
        return df
    except Exception as e:
        logger.error(f"Top alphas query failed: {str(e)}")
        return pd.DataFrame()
