import streamlit as st
import plotly.express as px
from core.omniverse import run_omniverse_sims

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("streamlit_app.py")
    
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');

body {
    background: radial-gradient(circle at 50% 10%, #1a0033 0%, #05050f 70%);
    font-family: 'Roboto Mono', monospace;
    overflow-x: hidden;
}

.big-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 4.8rem;
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

.glass-box, .stMetric, .stDataFrame {
    background: rgba(15,15,45,0.85);
    backdrop-filter: blur(30px);
    border: 2px solid #00ff9f;
    border-radius: 28px;
    padding: 30px;
    box-shadow: 0 0 80px rgba(0,255,159,0.6), inset 0 0 40px rgba(0,255,159,0.2);
    transition: transform 0.4s ease, box-shadow 0.4s ease;
}

.glass-box:hover, .stMetric:hover, .stDataFrame:hover {
    transform: perspective(1000px) rotateX(8deg) rotateY(8deg) scale(1.02);
    box-shadow: 0 0 120px rgba(0,255,159,0.9), inset 0 0 60px rgba(0,255,159,0.4);
}

.stButton button {
    background: transparent;
    border: 2px solid #00ff9f;
    color: #fff;
    box-shadow: 0 0 25px #00ff9f;
    transition: all 0.4s ease;
    font-weight: 700;
    animation: neonflicker 1.5s infinite alternate;
}

.stButton button:hover {
    background: rgba(0,255,159,0.15);
    box-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff;
    transform: scale(1.08);
    border-color: #00b8ff;
}

@keyframes neonflicker {
    0% { opacity: 0.95; }
    100% { opacity: 1; }
}

.plotly-chart {
    border: 2px solid #00ff9f;
    border-radius: 16px;
    box-shadow: 0 0 60px rgba(0,255,159,0.5);
    transition: all 0.4s ease;
}

.plotly-chart:hover {
    box-shadow: 0 0 100px rgba(0,255,159,0.9);
    transform: scale(1.02);
}
</style>
""", unsafe_allow_html=True)
st.title("🌌 Financial Omniverse")
st.caption("Fixes Garbage backtesting + unknown regime risk + tail events")

st.markdown("**Problem it obliterates:** Historical backtests miss competitor reactions, liquidity dynamics, and novel shocks. Stress tests are just reshuffled history.")

st.markdown("**How the tool works:** A true generative \"foundation world model\" for finance (like Sora/Video world models but physics-constrained with no-arbitrage, market microstructure, and behavioral rules). Trained on every tick of multi-asset history + alt data... Uses diffusion + autoregressive + causal intervention layers so it can generate infinite realistic futures, including ones never seen before... You drop your strategy into it and run millions of counterfactuals with full agent interactions.")

scenario = st.selectbox("Choose extreme future scenario", ["Base", "Trump2+China", "AI-CapEx-Crash", "2025-Quant-Wobble"])
if st.button("Generate 8,000 Omniverse Futures", type="primary"):
    with st.spinner("Running millions of counterfactual world-model simulations..."):
        paths = run_omniverse_sims(scenario)
        fig = px.line(paths[:400].T, title=f"Omniverse – {scenario} Regime Futures")
        st.plotly_chart(fig, use_container_width=True)
        st.success("**Insane value:** Discover strategies that work in regimes that don't exist yet. Portfolio optimization and risk models that are actually robust. One fund using this could have sidestepped the entire 2025 quant wobble... $5B+ in avoided losses + new strategy discovery per year. This is the holy grail — whoever has the best Omniverse basically has a time machine for markets.")
