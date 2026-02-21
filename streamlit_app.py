import streamlit as st
from core.registry import get_top_alphas
from core.evo_factory import evolve_new_alpha

st.set_page_config(page_title="MOONSHOT", layout="wide", page_icon="🌑", initial_sidebar_state="collapsed")

# CYBERPUNK STYLE - GLOWING NEON TITLES
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');

body {
    background: radial-gradient(circle at 50% 10%, #1a0033 0%, #05050f 70%);
    font-family: 'Roboto Mono', monospace;
}

.big-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 5rem;
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
</style>
""", unsafe_allow_html=True)

# LOGIN PROTECTION
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<p class="big-title" style="text-align:center">🌑 MOONSHOT</p>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align:center; color:#00ff9f;">ACCESS CONTROLLED</h2>', unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="harry / andy / daniel", autocomplete="off")
    password = st.text_input("Password", type="password", placeholder="Enter password", autocomplete="off")

    if st.button("LOGIN", type="primary", use_container_width=True):
        users = {
            "harry": "moonshot2026",
            "andy": "andy2026",
            "daniel": "daniel2026"
        }
        if username.lower() in users and password == users[username.lower()]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password")
else:
    st.markdown('<p class="big-title" style="text-align:center">🌑 MOONSHOT</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Alphas Evolved Live", "∞", "24/7")
    with col2: st.metric("Highest Persistence", "6.87", "↑")
    with col3: st.metric("Crowding Risk", "0.2%", "↓98%")
    with col4: st.metric("Omniverse Futures", "487M", "live")

    st.subheader("The Five Weapons")
    cols = st.columns(5)
    modules = [
        ("ShadowCrowd Oracle", "pages/01_🌑_ShadowCrowd_Oracle.py"),
        ("CausalForge Engine", "pages/02_🔬_CausalForge_Engine.py"),
        ("Financial Omniverse", "pages/03_🌌_Financial_Omniverse.py"),
        ("EvoAlpha Factory", "pages/04_🧬_EvoAlpha_Factory.py"),
        ("Liquidity Teleporter", "pages/05_⚡_Liquidity_Teleporter.py"),
        ("Live Alpha Execution Lab", "pages/06_📈_Live_Alpha_Execution_Lab.py")
    ]
    for col, (name, page) in zip(cols, modules):
        with col:
            if st.button(name, use_container_width=True, type="primary", key=name):
                st.switch_page(page)

    st.markdown("---")
    st.subheader("Live Alpha Zoo")
    st.dataframe(get_top_alphas(25), use_container_width=True, hide_index=True)

    if st.button("Refresh Zoo", type="primary"):
        st.rerun()
