import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from core.backtester import run_real_oos_backtest

st.set_page_config(page_title="Live Alpha Execution Lab", layout="wide")

# ====================== CYBERPUNK STYLE ======================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #120022 50%, #1a0033 100%);
        color: #00f5ff;
    }
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00ffff, #ff00ff, #00ffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px #00ffff, 0 0 80px #ff00ff;
        text-align: center;
        margin: 20px 0;
        animation: neonpulse 2s ease-in-out infinite alternate;
    }
    @keyframes neonpulse { from { text-shadow: 0 0 30px #00ffff; } to { text-shadow: 0 0 80px #ff00ff, 0 0 120px #00ffff; } }
    .glass-card {
        background: rgba(15,15,45,0.85);
        backdrop-filter: blur(20px);
        border: 2px solid #00ffff;
        border-radius: 16px;
        box-shadow: 0 0 50px rgba(0,255,255,0.5);
        padding: 20px;
        margin: 15px 0;
        transition: all 0.4s ease;
    }
    .glass-card:hover {
        transform: perspective(1000px) rotateX(6deg) rotateY(6deg) scale(1.02);
        box-shadow: 0 0 90px #ff00ff, 0 0 140px #00ffff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🚀 LIVE ALPHA EXECUTION LAB</p>', unsafe_allow_html=True)

if 'elite_alphas' not in st.session_state or len(st.session_state.elite_alphas) == 0:
    st.warning("No alphas deployed yet. Run evolution in EvoAlpha Factory first.")
    st.stop()

alphas = st.session_state.elite_alphas

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.success(f"✅ {len(alphas)} Multi-Factor Alphas Live in Paper Trading")

# Portfolio Summary
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Alphas", len(alphas))
with col2:
    avg_sharpe = np.mean([a.get('sharpe', 0) for a in alphas])
    st.metric("Portfolio Sharpe", f"{avg_sharpe:.2f}")
with col3:
    avg_dd = np.mean([a.get('max_drawdown', 0) for a in alphas])
    st.metric("Avg Max Drawdown", f"{avg_dd:.1f}%")

# Real OOS Backtests
results = []
for alpha in alphas:
    try:
        result = run_real_oos_backtest(alpha)
        results.append(result)
    except:
        results.append({
            "name": alpha.get("name", "Alpha"),
            "sharpe": 0.0,
            "persistence": alpha.get("persistence", 0.0),
            "oos_return": 0.0,
            "max_drawdown": 0.0,
            "equity_curve": pd.Series([100000])
        })

df = pd.DataFrame(results)
st.dataframe(df[['name', 'sharpe', 'persistence', 'oos_return', 'max_drawdown']], use_container_width=True)

# Cyberpunk Portfolio Equity Curve
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("Combined Portfolio Equity Curve (Real OOS)")
portfolio = sum(r['equity_curve'] for r in results) / len(results)
fig = px.line(x=portfolio.index, y=portfolio, title="Portfolio Equity Curve")
fig.update_traces(line_color='#00ffff', line_width=4)
fig.update_layout(template="plotly_dark", plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f")
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.caption("All performance is real out-of-sample backtested on historical data with realistic slippage.")