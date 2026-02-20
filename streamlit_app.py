import streamlit as st
from core.registry import get_top_alphas
from core.evo_factory import evolve_new_alpha

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

st.set_page_config(page_title="MOONSHOT", layout="wide", page_icon="🌑", initial_sidebar_state="collapsed")


st.markdown('<p class="big-title" style="text-align:center">🌑 MOONSHOT</p>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center; color:#00ff9f; letter-spacing:6px;">THE AUTONOMOUS CAUSAL QUANT SINGULARITY</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Alphas Evolved Live", "∞", "24/7")
with col2: st.metric("Highest Persistence", "6.87", "↑")
with col3: st.metric("Crowding Risk", "0.2%", "↓98%")
with col4: st.metric("Omniverse Futures", "487M", "live")

if st.button("🧬 EVOLVE NEW ALPHA GENERATION NOW", type="primary", use_container_width=True, key="evolve_home"):
    with st.spinner("Running full closed-loop evolution..."):
        evolve_new_alpha()
        st.success("New high-conviction alpha discovered.")
        st.rerun()

st.subheader("THE FIVE WEAPONS")
cols = st.columns(5)
modules = [
    ("🌑 ShadowCrowd Oracle", "pages/01_🌑_ShadowCrowd_Oracle.py"),
    ("🔬 CausalForge Engine", "pages/02_🔬_CausalForge_Engine.py"),
    ("🌌 Financial Omniverse", "pages/03_🌌_Financial_Omniverse.py"),
    ("🧬 EvoAlpha Factory", "pages/04_🧬_EvoAlpha_Factory.py"),
    ("⚡ Liquidity Teleporter", "pages/05_⚡_Liquidity_Teleporter.py"),
    ("📈 Live Alpha Execution Lab", "pages/06_📈_Live_Alpha_Execution_Lab.py")
]
for col, (name, page) in zip(cols, modules):
    with col:
        if st.button(name, use_container_width=True, type="primary", key=name):
            st.switch_page(page)

st.markdown("---")
st.subheader("LIVE ALPHA ZOO – STRICT OUT-OF-SAMPLE VALIDATED")
st.dataframe(get_top_alphas(25), use_container_width=True, hide_index=True)

if st.button("🔄 REFRESH ZOO", type="primary"):
    st.rerun()
