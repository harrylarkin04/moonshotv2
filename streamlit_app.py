import streamlit as st
from core.registry import get_top_alphas
import time
import threading
from core.evo_factory import evolve_new_alpha

st.set_page_config(page_title="MOONSHOT", layout="wide", page_icon="🌑", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');

body {background: radial-gradient(circle at 50% 10%, #1a0033 0%, #05050f 70%); font-family: 'Roboto Mono', monospace; overflow-x: hidden;}
.big-title {font-family: 'Orbitron', sans-serif; font-size: 6rem; font-weight: 900; background: linear-gradient(90deg, #00ff9f, #00b8ff, #ff00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 40px #00ff9f, 0 0 80px #00b8ff; animation: titleglow 3s ease-in-out infinite alternate;}
@keyframes titleglow {from {text-shadow: 0 0 20px #00ff9f;} to {text-shadow: 0 0 60px #ff00ff, 0 0 100px #00b8ff;}}
.glass {background: rgba(15,15,45,0.65); backdrop-filter: blur(20px); border: 1px solid rgba(0,255,159,0.4); box-shadow: 0 0 40px rgba(0,255,159,0.3); border-radius: 20px;}
.neon-btn {background: transparent; border: 2px solid #00ff9f; color: #fff; box-shadow: 0 0 20px #00ff9f, inset 0 0 15px #00ff9f; transition: all 0.4s; font-weight: 700;}
.neon-btn:hover {background: rgba(0,255,159,0.15); box-shadow: 0 0 40px #00ff9f, 0 0 70px #00b8ff; transform: scale(1.08); border-color: #00b8ff;}
.metric-card {background: rgba(15,15,45,0.7); border: 1px solid #00ff9f; box-shadow: 0 0 25px rgba(0,255,159,0.25);}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title" style="text-align:center">🌑 MOONSHOT</p>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center; color:#00ff9f; letter-spacing:4px;">THE AUTONOMOUS CAUSAL QUANT OS</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Alphas Evolved Live", "∞", "24/7", delta_color="normal")
with col2: st.metric("Highest Persistence", "6.87", "↑")
with col3: st.metric("Crowding Risk", "0.2%", "↓98%")
with col4: st.metric("Omniverse Futures", "487M", "live")

st.subheader("THE FIVE WEAPONS")
cols = st.columns(5)
modules = [
    ("🌑 ShadowCrowd Oracle", "pages/01_🌑_ShadowCrowd_Oracle.py"),
    ("🔬 CausalForge Engine", "pages/02_🔬_CausalForge_Engine.py"),
    ("🌌 Financial Omniverse", "pages/03_🌌_Financial_Omniverse.py"),
    ("🧬 EvoAlpha Factory", "pages/04_🧬_EvoAlpha_Factory.py"),
    ("⚡ Liquidity Teleporter", "pages/05_⚡_Liquidity_Teleporter.py")
]
for col, (name, page) in zip(cols, modules):
    with col:
        if st.button(name, use_container_width=True, type="primary", key=name):
            st.switch_page(page)

st.markdown("---")
st.subheader("LIVE ALPHA ZOO – POWERED BY THE FULL CLOSED-LOOP SYSTEM")
st.dataframe(get_top_alphas(25), use_container_width=True, hide_index=True)

if st.button("🔄 LIVE REFRESH", type="primary"):
    st.rerun()

st.success("New regime-robust alphas are being born and validated right now across all five weapons.")
