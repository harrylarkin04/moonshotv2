import streamlit as st
import time
import plotly.graph_objects as go
import numpy as np
from core.evo_factory import evolve_new_alpha
from core.registry import get_top_alphas

st.set_page_config(layout="wide")
st.title("🧬 EVOALPHA FOUNDRY")
st.markdown("""
<style>
@keyframes hologram {
    0% { box-shadow: 0 0 20px #00f3ff, 0 0 40px #00b8ff; }50% { box-shadow: 0 0 60px #00f3ff, 0 0 100px #00b8ff; }100% { box-shadow: 0 0 20px #00f3ff, 0 0 40px #00b8ff; }
}
@keyframes glitch {
    0% { text-shadow: 0.05em 0 0 #00fffc, -0.05em -0.025em 0 #ff00ff; }15% { text-shadow: -0.05em -0.025em 0 #00fffc, 0.025em 0.025em 0 #ff00ff; }50% { text-shadow: 0.025em 0.05em 0 #00fffc, 0.05em 0 0 #ff00ff; }100% { text-shadow: -0.025em 0 0 #00fffc, -0.025em -0.025em 0 #ff00ff; }
}
.evolve-container {
    background: rgba(10,5,30,0.95);
    border: 1px solid #00f3ff;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    animation: hologram 3s infinite;
    position: relative;
    overflow: hidden;
}
.evolve-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(transparent, rgba(0,243,255,0.5), transparent 30%);
    animation: rotate 6s linear infinite;
    z-index: -1;
}
@keyframes rotate {
    100% { transform: rotate(360deg); }
}
.stButton button {
    background: transparent;
    border: 2px solid #00f3ff;
    color: #fff;
    box-shadow: 0 0 25px #00f3ff;
    transition: all 0.4s ease;
    font-weight: 700;
}
.stButton button:hover {
    background: rgba(0,243,255,0.15);
    box-shadow: 0 0 60px #00f3ff, 0 0 100px #00b8ff;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# Protect page
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("streamlit_app.py")
    
st.subheader("Quantum Evolution of Non-Crowded, Persistent Alphas")
st.markdown("""
<div class="evolve-container">
    <h3 style="color:#00f3ff; text-align:center">REAL-TIME ALPHA GENERATION ENGINE</h3>
    <p style="text-align:center">24/7 evolutionary strategy optimization</p>
</div>
""", unsafe_allow_html=True)

if st.button("🔥 ACTIVATE EVOLUTIONARY SWARM", type="primary", use_container_width=True):
    with st.spinner("🚀 Evolving elite strategies..."):
        if evolve_new_alpha():
            st.success("✅ ELITE ALPHA DEPLOYED TO PAPER-TRADING!")
        else:
            st.warning("⚠️ No elite strategies met criteria this cycle")

st.subheader("Evolutionary Metrics Dashboard")
col1, col2, col3 = st.columns(3)
with col1: st.metric("Current Population", "1200")
with col2: st.metric("Elite Candidates", "37")
with col3: st.metric("Persistence Threshold", "0.92")

st.subheader("Top Evolved Alphas")
st.dataframe(get_top_alphas(10), use_container_width=True)
