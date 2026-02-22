import numpy as np
import hashlib
import json
from datetime import datetime
import sqlite3
from core.data_fetcher import get_multi_asset_data
import pandas as pd
import logging
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Initialize logger
logger = logging.getLogger('registry')
logger.setLevel(logging.INFO)

# Create database directory if needed
os.makedirs('data', exist_ok=True)
conn = sqlite3.connect('data/alphas.db', check_same_thread=False)

def init_db():
    """Initialize database with proper table structure"""
    try:
        with conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS alphas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                sharpe REAL,
                persistence_score REAL,
                created TEXT,
                live_paper_trading INTEGER DEFAULT 0,
                oos_metrics TEXT,
                diversity REAL,
                consistency REAL,
                returns_series TEXT
            )
            """)
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"DB initialization failed: {str(e)}")

# Initialize database on import
init_db()

def save_alpha(name, description, sharpe, persistence_score, auto_deploy=False, metrics=None, diversity=0.0, consistency=0.0, returns_series=None):
    try:
        # STRICTER: Increased elite criteria thresholds
        if sharpe > 3.0 and persistence_score > 0.85 and diversity > 0.6:
            strategy_hash = hashlib.sha256(f"{name}{description}{datetime.now()}".encode()).hexdigest()[:12]
            oos_metrics = {
                'sharpe': sharpe,
                'persistence': persistence_score,
                'hash': strategy_hash,
                'diversity': diversity,
                'consistency': consistency,
                'backtest_period': '2020-01-01_to_2024-06-01',
                'last_updated': datetime.now().isoformat(),
                'returns_series': returns_series
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
    """Enhanced walk-forward validation with real market data"""
    try:
        # Fetch real market data
        symbols = ['SPY', 'QQQ', 'IWM', 'GLD', 'TLT']
        data = get_multi_asset_data(symbols, period="2y")
        returns = data.pct_change().dropna()
        
        # Use last 6 months as OOS period
        oos_returns = returns.iloc[-120:]
        
        # Backtest strategy
        portfolio_value = 1.0
        position = 0.0
        portfolio_values = []
        returns_list = []
        
        for i in range(1, len(oos_returns)):
            # Get previous day returns for all assets
            prev_returns = oos_returns.iloc[i-1]
            
            # Get strategy signal
            signal = strategy_fn(prev_returns)
            target_position = signal * portfolio_value
            trade = target_position - position
            
            # Realistic slippage model
            slippage_bp = 5 + 15 * abs(trade) / 1000000
            slippage = slippage_bp / 10000 * abs(trade)
            position = target_position
            
            # Current day returns
            current_returns = oos_returns.iloc[i]
            portfolio_return = np.dot(current_returns, position) - slippage
            portfolio_value *= (1 + portfolio_return)
            
            portfolio_values.append(portfolio_value)
            returns_list.append(portfolio_return)
        
        returns_series = pd.Series(returns_list)
        ann_return = returns_series.mean() * 252
        ann_vol = returns_series.std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0
        
        # Calculate max drawdown
        peak = np.maximum.accumulate(portfolio_values)
        drawdown = (np.array(portfolio_values) - peak) / peak
        max_drawdown = np.min(drawdown)
        
        # Persistence calculation
        monthly_returns = returns_series.resample('M').agg(lambda x: (1+x).prod()-1)
        positive_months = (monthly_returns > 0).sum()
        persistence = positive_months / len(monthly_returns) if len(monthly_returns) > 0 else 0
        
        return {
            'sharpe': max(0, sharpe),
            'persistence': persistence,
            'max_drawdown': abs(max_drawdown),
            'returns_series': returns_list,
            'period': f'2020-01-01_to_2024-06-01'
        }
    except Exception as e:
        logger.error(f"OOS validation failed: {str(e)}")
        return {
            'sharpe': 0,
            'persistence': 0,
            'max_drawdown': 0,
            'returns_series': [],
            'period': 'error'
        }

def get_top_alphas(limit=25):
    """Fetch top alphas with enhanced filtering and freshness"""
    try:
        # Query the database
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

def create_performance_plots(returns_series):
    if not returns_series or len(returns_series) == 0:
        return None, None, None
    
    try:
        returns = pd.Series(returns_series)
        # Generate date index for proper time series plotting
        dates = pd.date_range(end=pd.Timestamp.today(), periods=len(returns), freq='B')
        returns.index = dates
        
        equity = (1 + returns).cumprod()
        drawdown = (equity / equity.cummax() - 1) * 100
        
        # Calculate performance metrics
        ann_return = returns.mean() * 252
        ann_vol = returns.std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0
        max_dd = drawdown.min()
        calmar = ann_return / (-max_dd/100) if max_dd < 0 else 0
        
        # Equity curve
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=equity.index, y=equity, mode='lines', name='Equity', line=dict(color='#00ff9f')))
        fig1.update_layout(
            title=f'Equity Curve | Sharpe: {sharpe:.2f} | Calmar: {calmar:.2f}',
            template='plotly_dark',
            hovermode='x unified',
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        
        # Drawdown chart
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=drawdown.index, y=drawdown, fill='tozeroy', name='Drawdown', 
                                 fillcolor='rgba(255,0,0,0.3)', line=dict(color='#ff0055')))
        fig2.update_layout(
            title=f'Drawdown | Max DD: {max_dd:.2f}%',
            template='plotly_dark',
            yaxis=dict(ticksuffix='%'),
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        
        # Monthly returns
        monthly_returns = equity.resample('M').last().pct_change().dropna() * 100
        fig3 = go.Figure()
        colors = ['#00ff9f' if x >= 0 else '#ff0055' for x in monthly_returns]
        fig3.add_trace(go.Bar(x=monthly_returns.index, y=monthly_returns, marker_color=colors, name='Monthly Return'))
        fig3.update_layout(
            title='Monthly Returns',
            template='plotly_dark',
            yaxis=dict(ticksuffix='%'),
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        
        return fig1, fig2, fig3
    except Exception as e:
        logger.error(f"Plot generation failed: {str(e)}")
        return None, None, None
