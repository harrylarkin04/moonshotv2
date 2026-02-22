import streamlit as st
import plotly.express as px
import pandas as pd
from core.backtester import run_real_oos_backtest

st.set_page_config(page_title="Live Alpha Execution Lab", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #120022 50%, #1a0033 100%); color: #00f5ff; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 4.5rem; font-weight: 900; background: linear-gradient(90deg, #00ffff, #ff00ff, #00ffff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 40px #00ffff, 0 0 80px #ff00ff; text-align: center; margin: 20px 0; animation: neonpulse 2s infinite alternate; }
    @keyframes neonpulse { from { text-shadow: 0 0 30px #00ffff; } to { text-shadow: 0 0 80px #ff00ff, 0 0 120px #00ffff; } }
    .glass-card { background: rgba(15,15,45,0.85); backdrop-filter: blur(20px); border: 2px solid #00ffff; border-radius: 16px; box-shadow: 0 0 50px rgba(0,255,255,0.5); padding: 20px; margin: 15px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">LIVE ALPHA EXECUTION LAB</p>', unsafe_allow_html=True)

if 'elite_alphas' not in st.session_state or len(st.session_state.elite_alphas) == 0:
    st.warning("No alphas yet. Run evolution in EvoAlpha Factory first.")
    st.stop()

alphas = st.session_state.elite_alphas

st.success(f"Running real OOS backtests on {len(alphas)} alphas...")

results = []
for alpha in alphas:
    result = run_real_oos_backtest(alpha)
    results.append(result)

df = pd.DataFrame(results)
st.dataframe(df[['name', 'sharpe', 'persistence', 'oos_return', 'max_drawdown']], use_container_width=True)

st.subheader("Combined Portfolio Equity Curve (Real OOS)")
portfolio = sum(r['equity_curve'] for r in results) / len(results)
fig = px.line(x=portfolio.index, y=portfolio, title="Portfolio Equity Curve")
fig.update_traces(line_color='#00ffff', line_width=4)
fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.caption("Real out-of-sample backtested performance on historical data.")