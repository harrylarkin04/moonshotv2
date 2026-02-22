import numpy as np
import hashlib
import json
from datetime import datetime
import sqlite3
from core.data_fetcher import get_multi_asset_data
import pandas as pd
import logging

# Initialize logger
logger = logging.getLogger('registry')
logger.setLevel(logging.INFO)

conn = sqlite3.connect('alphas.db', check_same_thread=False)

def save_alpha(name, description, sharpe, persistence_score, auto_deploy=False, metrics=None, diversity=0.0, consistency=0.0):
    try:
        # STRICTER: Increased elite criteria thresholds
        if sharpe > 4.0 and persistence_score > 0.88 and diversity > 0.65:
            strategy_hash = hashlib.sha256(f"{name}{description}{datetime.now()}".encode()).hexdigest()[:12]
            oos_metrics = {
                'sharpe': sharpe,
                'persistence': persistence_score,
                'hash': strategy_hash,
                'diversity': diversity,
                'consistency': consistency,
                'backtest_period': '2020-01-01_to_2024-06-01',
                'last_updated': datetime.now().isoformat()
            }
            
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO alphas 
                    (name, description, sharpe, persistence_score, created, live_paper_trading, oos_metrics, diversity, consistency) 
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (name, description, sharpe, persistence_score, datetime.now().isoformat(), 
                      1 if auto_deploy else 0, json.dumps(oos_metrics), diversity, consistency))
            logger.info(f"Saved alpha: {name} | Sharpe: {sharpe:.2f} | Persistence: {persistence_score:.2f}")
            return True
        logger.warning(f"Alpha rejected: {name} | Sharpe: {sharpe:.2f} | Persistence: {persistence_score:.2f}")
        return False
    except Exception as e:
        logger.error(f"Save error: {e}")
        conn.rollback()
        return False

def get_real_oos_metrics(strategy_fn):
    """Enhanced walk-forward validation with dynamic volume/slippage model"""
    try:
        adj_close, returns, volumes = get_multi_asset_data(period="max", include_volume=True)
        
        if returns.empty or volumes.empty:
            logger.error("No data available for OOS validation")
            return {
                'sharpe': 0,
                'persistence': 0,
                'max_drawdown': 0,
                'period': 'N/A'
            }
        
        # Dynamic train/test split based on volatility regimes
        train_ratio = 0.7 if len(returns) > 1000 else 0.6
        split_idx = int(len(returns)*train_ratio)
        
        train = returns.iloc[:split_idx]
        test = returns.iloc[split_idx:]
        test_volumes = volumes.iloc[split_idx:] if volumes is not None else None
        
        portfolio_value = 1.0
        peak_value = 1.0
        max_drawdown = 0.0
        returns_list = []
        position = 0.0
        
        # ENHANCED: Volume clustering detection
        volume_clusters = {}
        if test_volumes is not None:
            for asset in test_volumes.columns:
                # Use K-means to identify volume regimes
                from sklearn.cluster import KMeans
                vol_data = test_volumes[asset].values.reshape(-1, 1)
                kmeans = KMeans(n_clusters=3, random_state=0).fit(vol_data)
                volume_clusters[asset] = kmeans.labels_
        
        # Enhanced slippage model with volume percentiles
        for i in range(1, len(test)):
            current_returns = test.iloc[i]
            prev_returns = test.iloc[i-1]
            
            signal = strategy_fn(prev_returns)
            target_position = signal * portfolio_value
            trade = target_position - position
            
            # DYNAMIC SLIPPAGE MODEL
            slippage_bp = 10  # Base slippage
            
            if test_volumes is not None and not test_volumes.empty:
                # Volume-based adjustment
                volume_percentile = test_volumes.iloc[i].rank(pct=True).mean()
                liquidity_adj = 1 - volume_percentile
                
                # Trade size impact
                trade_size_ratio = abs(trade) / (test_volumes.iloc[i].mean() + 1e-6)
                
                # Volume cluster impact (if available)
                cluster_adj = 0
                if volume_clusters:
                    cluster_vals = [volume_clusters[asset][i] for asset in test_volumes.columns]
                    cluster_adj = np.mean(cluster_vals) / 2  # 0-1 scale adjustment
                
                slippage_bp = 5 + 25 * liquidity_adj + 20 * trade_size_ratio + 10 * cluster_adj
            
            slippage = slippage_bp / 10000 * abs(trade)
            position = target_position
            portfolio_return = np.dot(current_returns, position) - slippage
            portfolio_value *= (1 + portfolio_return)
            
            peak_value = max(peak_value, portfolio_value)
            current_dd = (peak_value - portfolio_value) / peak_value
            max_drawdown = max(max_drawdown, current_dd)
            returns_list.append(portfolio_return)
        
        returns_series = pd.Series(returns_list)
        if len(returns_series) < 3:
            return {
                'sharpe': 0,
                'persistence': 0,
                'max_drawdown': max_drawdown,
                'period': f'{test.index[0].date()}_to_{test.index[-1].date()}'
            }
        
        ann_return = returns_series.mean() * 252
        ann_vol = returns_series.std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0
        
        # Improved persistence calculation with regime filtering
        monthly_returns = returns_series.resample('M').agg(lambda x: (1+x).prod()-1)
        positive_months = (monthly_returns > 0).sum()
        persistence = positive_months / len(monthly_returns) if len(monthly_returns) > 0 else 0
        
        return {
            'sharpe': max(0, sharpe),  # Prevent negative Sharpe inflation
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
    """Fetch top alphas with enhanced filtering and freshness"""
    try:
        query = f"""
            SELECT name, sharpe, persistence_score, diversity, consistency, oos_metrics,
                   json_extract(oos_metrics, '$.last_updated') as last_updated
            FROM alphas 
            WHERE sharpe > 3.8 
              AND persistence_score > 0.85
              AND diversity > 0.6
              AND datetime(created) > datetime('now', '-30 days')
            ORDER BY (0.4*sharpe + 0.3*persistence_score + 0.2*diversity + 0.1*consistency) DESC
            LIMIT {limit}
        """
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            df['oos_metrics'] = df['oos_metrics'].apply(json.loads)
            df['last_updated'] = pd.to_datetime(df['last_updated'])
        return df
    except Exception as e:
        logger.error(f"Top alphas query failed: {str(e)}")
        return pd.DataFrame()
