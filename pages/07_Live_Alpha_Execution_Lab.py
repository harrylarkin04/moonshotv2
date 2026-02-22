import streamlit as st
import numpy as np
import pandas as pd
import json
from core.registry import get_top_alphas
from core.data_fetcher import get_multi_asset_data

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');
body { background: radial-gradient(circle at 50% 10%, #1a0033 0%, #05050f 70%); font-family: 'Roboto Mono', monospace; }
.big-title { font-family: 'Orbitron', sans-serif; font-size: 5.2rem; font-weight: 900; background: linear-gradient(90deg, #00ff9f, #00b8ff, #ff00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 40px #00ff9f, 0 0 80px #00b8ff, 0 0 120px #ff00ff; animation: neonpulse 2s ease-in-out infinite alternate; }
@keyframes neonpulse { from { text-shadow: 0 0 20px #00ff9f, 0 0 40px #00b8ff; } to { text-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff, 0 0 140px #ff00ff; } }
.glass, .stMetric, .stDataFrame, .plotly-chart { background: rgba(15,15,45,0.85); backdrop-filter: blur(30px); border: 2px solid #00ff9f; border-radius: 16px; box-shadow: 0 0 60px rgba(0,255,159,0.5); transition: all 0.4s ease; }
.glass:hover, .stMetric:hover, .stDataFrame:hover, .plotly-chart:hover { transform: perspective(1000px) rotateX(8deg) rotateY(8deg) scale(1.02); box-shadow: 0 0 100px rgba(0,255,159,0.9); }
.stButton button { background: transparent; border: 2px solid #00ff9f; color: #fff; box-shadow: 0 0 25px #00ff9f; transition: all 0.4s ease; font-weight: 700; }
.stButton button:hover { background: rgba(0,255,159,0.15); box-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff; transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("streamlit_app.py")

st.title("📈 Live Alpha Execution Lab")
st.caption("Real-time backtesting with slippage and transaction costs")

alphas = get_top_alphas(10)

for _, alpha in alphas.iterrows():
    st.subheader(f"Alpha: {alpha['name']}")
    metrics = alpha.get('oos_metrics', {})
    if isinstance(metrics, str):
        try:
            metrics = json.loads(metrics)
        except:
            metrics = {}
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sharpe Ratio", f"{alpha['sharpe']:.2f}")
        st.metric("Diversity", f"{alpha['diversity']:.2f}")
    with col2:
        st.metric("Persistence Score", f"{alpha['persistence_score']:.2f}")
        st.metric("Consistency", f"{alpha['consistency']:.2f}")
    
    if metrics:
        st.caption("OOS Metrics:")
        st.json(metrics)
    
    st.divider()
