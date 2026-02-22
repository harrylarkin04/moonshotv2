import streamlit as st

# ====================== CONFIG ======================
st.set_page_config(
    page_title="Moonshot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== STABLE CYBERPUNK STYLE ======================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0a0a0f 0%, #1a0033 100%);
        color: #00f5ff;
    }
    h1 {
        text-shadow: 0 0 15px #00ffff, 0 0 30px #ff00ff;
        animation: none !important;
    }
    .stButton button {
        background: transparent;
        border: 2px solid #ff00ff;
        color: #00ffff;
    }
    .stButton button:hover {
        box-shadow: 0 0 25px #ff00ff;
        background: #ff00ff;
        color: #0a0a0f;
    }
</style>
""", unsafe_allow_html=True)

# ====================== SIMPLE LOGIN FOR JOSEPH ======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🚀 Moonshot")
    st.subheader("Quant Trading Intelligence Platform")

    username = st.text_input("Username", placeholder="")
    password = st.text_input("Password", type="password", placeholder="")

    if st.button("Login", type="primary"):
        if username == "joseph" and password == "moonshot2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong credentials")
    st.stop()

# ====================== MAIN APP ======================
st.title("🚀 Moonshot")
st.markdown("**Next-generation closed-loop quant trading platform**")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🌌 CausalForge Engine", use_container_width=True):
        st.switch_page("pages/02_CausalForge_Engine.py")

with col2:
    if st.button("🔥 EvoAlpha Factory", use_container_width=True):
        st.switch_page("pages/04_EvoAlpha_Factory.py")

with col3:
    if st.button("📈 Live Alpha Execution Lab", use_container_width=True):
        st.switch_page("pages/07_Live_Alpha_Execution_Lab.py")

st.divider()

col4, col5, col6 = st.columns(3)

with col4:
    if st.button("👥 ShadowCrowd Oracle", use_container_width=True):
        st.switch_page("pages/01_ShadowCrowd_Oracle.py")

with col5:
    if st.button("🌌 Financial Omniverse", use_container_width=True):
        st.switch_page("pages/03_Financial_Omniverse.py")

with col6:
    if st.button("💰 Impact Dashboard", use_container_width=True):
        st.switch_page("pages/06_Impact_Dashboard.py")

st.divider()

st.caption("Built for institutional-grade performance • All alphas evolved from real LLM causal hypotheses")