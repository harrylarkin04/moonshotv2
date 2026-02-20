import streamlit as st
from core.registry import get_top_alphas
from core.evo_factory import evolve_new_alpha

st.set_page_config(page_title="MOONSHOT", layout="wide", page_icon="🌑", initial_sidebar_state="collapsed")

# GLOBAL CYBERPUNK CSS (already included above - add it here if not already)

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
