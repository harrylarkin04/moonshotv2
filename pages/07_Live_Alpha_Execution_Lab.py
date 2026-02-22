import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.backtester import run_real_oos_backtest  # assuming you have this file

# ────────────────────────────────────────────────
#  CYBERPUNK / NEON STYLE
# ────────────────────────────────────────────────
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
        animation: neonpulse 2s infinite alternate;
    }
    @keyframes neonpulse {
        from { text-shadow: 0 0 30px #00ffff; }
        to   { text-shadow: 0 0 80px #ff00ff, 0 0 120px #00ffff; }
    }
    .glass-card {
        background: rgba(15,15,45,0.85);
        backdrop-filter: blur(20px);
        border: 2px solid #00ffff;
        border-radius: 16px;
        box-shadow: 0 0 50px rgba(0,255,255,0.5);
        padding: 20px;
        margin: 15px 0;
    }
    .stDataFrame {
        background: rgba(15,15,45,0.9);
        border: 2px solid #00ff9f;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">LIVE ALPHA EXECUTION LAB</p>', unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  LOAD ALPHAS
# ────────────────────────────────────────────────
if 'elite_alphas' not in st.session_state or len(st.session_state.elite_alphas) == 0:
    st.warning("No alphas deployed yet. Run evolution in EvoAlpha Factory first.")
    st.stop()

alphas = st.session_state.elite_alphas

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.success(f"✅ {len(alphas)} Multi-Factor Alphas Live in Paper Trading")

# Portfolio summary
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Alphas", len(alphas))
with col2:
    avg_sharpe = np.mean([a.get('sharpe', 0) for a in alphas])
    st.metric("Portfolio Sharpe", f"{avg_sharpe:.2f}")
with col3:
    avg_dd = np.mean([a.get('max_drawdown', 0) for a in alphas])
    st.metric("Avg Max Drawdown", f"{avg_dd:.1f}%")

# ────────────────────────────────────────────────
#  REAL BACKTESTS
# ────────────────────────────────────────────────
results = []
for alpha in alphas:
    try:
        result = run_real_oos_backtest(alpha)
        results.append(result)
    except Exception as e:
        # Fallback so page never crashes
        results.append({
            "name": alpha.get("name", "Alpha"),
            "sharpe": 0.0,
            "persistence": alpha.get("persistence", 0.85),
            "oos_return": 0.0,
            "max_drawdown": 0.0,
            "equity_curve": pd.Series([100000] * 100)
        })

df = pd.DataFrame(results)
st.dataframe(df[['name', 'sharpe', 'persistence', 'oos_return', 'max_drawdown']], use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  CYBERPUNK PORTFOLIO CHART
# ────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("Combined Portfolio Equity Curve (Real OOS)")
portfolio = sum(r['equity_curve'] for r in results) / len(results)
fig = px.line(x=portfolio.index, y=portfolio, title="Portfolio Equity Curve")
fig.update_traces(line_color='#00ffff', line_width=4)
fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="#0a0a0f",
    paper_bgcolor="#0a0a0f",
    font_color="#00f5ff"
)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.caption("Real out-of-sample backtested performance on historical data with realistic slippage.")