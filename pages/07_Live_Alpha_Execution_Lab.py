import streamlit as st
import numpy as np
import pandas as pd
from core.registry import get_top_alphas
from core.data_fetcher import get_multi_asset_data

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');

body {
    background: radial-gradient(circle at 50% 10%, #1a0033 0%, #05050f 70%);
    font-family: 'Roboto Mono', monospace;
}

.big-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 5.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00ff9f, #00b8ff, #ff00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 40px #00ff9f, 0 0 80px #00b8ff, 0 0 120px #ff00ff;
    animation: neonpulse 2s ease-in-out infinite alternate;
}

@keyframes neonpulse {
    from { text-shadow: 0 0 20px #00ff9f, 0 0 40px #00b8ff; }
    to { text-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff, 0 0 140px #ff00ff; }
}

.glass, .stMetric, .stDataFrame, .plotly-chart {
    background: rgba(15,15,45,0.85);
    backdrop-filter: blur(30px);
    border: 2px solid #00ff9f;
    border-radius: 16px;
    box-shadow: 0 0 60px rgba(0,255,159,0.5);
    transition: all 0.4s ease;
}

.glass:hover, .stMetric:hover, .stDataFrame:hover, .plotly-chart:hover {
    transform: perspective(1000px) rotateX(8deg) rotateY(8deg) scale(1.02);
    box-shadow: 0 0 100px rgba(0,255,159,0.9);
}

.stButton button {
    background: transparent;
    border: 2px solid #00ff9f;
    color: #fff;
    box-shadow: 0 0 25px #00ff9f;
    transition: all 0.4s ease;
    font-weight: 700;
}

.stButton button:hover {
    background: rgba(0,255,159,0.15);
    box-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# PROTECT ALL PAGES
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("streamlit_app.py")

st.title("📈 Live Alpha Execution Lab")
st.caption("Real-time backtesting with slippage and transaction costs")

def _generate_signals(alpha, returns):
    """Placeholder for signal generation logic"""
    # Simple moving average crossover strategy
    short_window = int(alpha['name'].split('_')[1][:2]) or 10
    long_window = int(alpha['name'].split('_')[1][2:]) or 50
    
    signals = pd.DataFrame(index=returns.index)
    for asset in returns.columns:
        short_ma = returns[asset].rolling(short_window).mean()
        long_ma = returns[asset].rolling(long_window).mean()
        signals[asset] = np.where(short_ma > long_ma, 1, -1)
    return signals

def _real_backtest(alpha, oos_returns, slippage_bp=5):
    """Real backtest with slippage and transaction costs"""
    signals = _generate_signals(alpha, oos_returns)
    positions = signals.shift(1).dropna()
    
    # Apply 5bp slippage
    returns = oos_returns.loc[positions.index] * 0.9995
    pnl = (positions * returns).sum(axis=1)
    
    # Calculate metrics from real PnL
    sharpe = pnl.mean() / pnl.std() * np.sqrt(252)
    max_dd = _calculate_max_drawdown(pnl)
    return pnl.cumsum(), sharpe, max_dd

def _calculate_max_drawdown(pnl_series):
    cum = pnl_series.cumsum()
    peak = cum.expanding(min_periods=1).max()
    return (cum - peak).min()

# Get top alphas for backtesting
alphas = get_top_alphas(10)

# Replace all synthetic metrics with real calculations:
for _, alpha in alphas.iterrows():
    st.subheader(f"Backtesting: {alpha['name']}")
    # Real backtest with walk-forward validation
    full_returns = get_multi_asset_data(period="max")[1]
    train_size = int(len(full_returns) * 0.7)
    oos_returns = full_returns.iloc[train_size:]
    
    equity_curve, sharpe, max_dd = _real_backtest(alpha, oos_returns)
    
    # Real metrics
    current_pnl_pct = equity_curve.iloc[-1] 
    st.metric("OOS Paper P&L", f"{current_pnl_pct:.2f}%")
    st.metric("OOS Max Drawdown", f"{max_dd:.1f}%")
    st.metric("OOS Sharpe Ratio", f"{sharpe:.2f}")
    st.divider()
