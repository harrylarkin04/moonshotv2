import streamlit as st
from core.registry import get_top_alphas

st.set_page_config(page_title="MOONSHOT", layout="wide", page_icon="🌑")

# ====================== YOUR ORIGINAL CYBERPUNK STYLE ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');
body { background: radial-gradient(circle at 50% 10%, #1a0033 0%, #05050f 70%); font-family: 'Roboto Mono', monospace; }
.big-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 5.5rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00ff9f, #00b8ff, #ff00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 40px #00ff9f, 0 0 80px #00b8ff, 0 0 140px #ff00ff;
    text-align: center;
    margin: 20px 0 10px 0;
    animation: neonpulse 1.8s ease-in-out infinite alternate;
}
@keyframes neonpulse { from { text-shadow: 0 0 30px #00ff9f, 0 0 60px #00b8ff; } to { text-shadow: 0 0 70px #00ff9f, 0 0 120px #00b8ff, 0 0 180px #ff00ff; } }

.glass-box {
    background: rgba(15,15,45,0.9);
    backdrop-filter: blur(30px);
    border: 2px solid #00ff9f;
    border-radius: 16px;
    box-shadow: 0 0 60px rgba(0,255,159,0.6);
    transition: all 0.4s ease;
}
.glass-box:hover {
    transform: perspective(1000px) rotateX(8deg) rotateY(8deg) scale(1.03);
    box-shadow: 0 0 110px rgba(0,255,159,0.9), 0 0 160px #ff00ff;
}
.stButton button {
    background: transparent;
    border: 2px solid #00ff9f;
    color: white;
    box-shadow: 0 0 25px #00ff9f;
    transition: all 0.4s ease;
    font-weight: 700;
}
.stButton button:hover {
    background: rgba(0,255,159,0.15);
    box-shadow: 0 0 70px #00ff9f, 0 0 120px #00b8ff, 0 0 160px #ff00ff;
    transform: scale(1.08);
}
</style>
""", unsafe_allow_html=True)

# ====================== LOGIN ======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<p class="big-title">🌑 MOONSHOT</p>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align:center; color:#00ff9f;">ACCESS CONTROLLED</h2>', unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="", autocomplete="off")
    password = st.text_input("Password", type="password", placeholder="", autocomplete="off")

    if st.button("ENTER THE GRID", type="primary", use_container_width=True):
        users = {"joseph": "moonshot2026", "harry": "moonshot2026"}
        if username.lower() in users and password == users[username.lower()]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# ====================== MAIN HOMEPAGE ======================
st.markdown('<p class="big-title">🌑 MOONSHOT</p>', unsafe_allow_html=True)

st.subheader("The Five Weapons")

cols = st.columns(5)

modules = [
    ("ShadowCrowd Oracle", "pages/01_ShadowCrowd_Oracle.py"),
    ("CausalForge Engine", "pages/02_CausalForge_Engine.py"),
    ("Financial Omniverse", "pages/03_Financial_Omniverse.py"),
    ("EvoAlpha Factory", "pages/04_EvoAlpha_Factory.py"),
    ("Liquidity Teleporter", "pages/05_Liquidity_Teleporter.py")
]

for col, (name, page) in zip(cols, modules):
    with col:
        if st.button(name, use_container_width=True, type="primary"):
            st.switch_page(page)

# Live Alpha Execution Lab button
if st.button("📈 Live Alpha Execution Lab", use_container_width=True, type="primary"):
    st.switch_page("pages/07_Live_Alpha_Execution_Lab.py")

st.divider()

st.subheader("Live Alpha Zoo")
st.dataframe(get_top_alphas(25), use_container_width=True, hide_index=True)

if st.button("Refresh Zoo", type="primary"):
    st.rerun()