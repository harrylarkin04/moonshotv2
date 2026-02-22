import streamlit as st

st.set_page_config(page_title="Moonshot", page_icon="🚀", layout="wide")

# ====================== PREMIUM CYBERPUNK STYLE ======================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #120022 50%, #1a0033 100%);
        color: #00f5ff;
    }
    .main-title {
        font-size: 5.2rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 12px;
        background: linear-gradient(90deg, #00ffff, #ff00ff, #00ffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 
            0 0 20px #00ffff,
            0 0 40px #ff00ff,
            0 0 80px #00ffff;
        text-align: center;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        font-size: 1.5rem;
        color: #a0f0ff;
        letter-spacing: 6px;
        margin-bottom: 50px;
    }
    .nav-button {
        background: rgba(255,255,255,0.03);
        border: 2px solid #00ffff;
        color: #00ffff;
        font-weight: bold;
        padding: 1.4rem 2rem;
        border-radius: 16px;
        transition: all 0.4s ease;
        text-align: center;
        font-size: 1.25rem;
        box-shadow: 0 0 15px rgba(0,255,255,0.3);
    }
    .nav-button:hover {
        background: linear-gradient(45deg, #ff00ff, #00ffff);
        color: #0a0a0f;
        box-shadow: 0 0 40px #ff00ff, 0 0 70px #00ffff;
        transform: translateY(-4px);
        border-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# ====================== LOGIN FOR JOSEPH ======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<h1 class="main-title">MOONSHOT</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">CLOSED-LOOP QUANT INTELLIGENCE PLATFORM</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Username", placeholder="")
        password = st.text_input("Password", type="password", placeholder="")

        if st.button("ENTER THE GRID", type="primary", use_container_width=True):
            if username.lower() == "joseph" and password == "moonshot2026":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")
    st.stop()

# ====================== MAIN HOMEPAGE ======================
st.markdown('<h1 class="main-title">MOONSHOT</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">NEXT-GENERATION QUANT TRADING SYSTEM</p>', unsafe_allow_html=True)

st.divider()

# Navigation Grid
col1, col2 = st.columns(2)

with col1:
    if st.button("🌌 CausalForge Engine", key="cf", use_container_width=True):
        st.switch_page("pages/02_CausalForge_Engine.py")
    if st.button("🔥 EvoAlpha Factory", key="evo", use_container_width=True):
        st.switch_page("pages/04_EvoAlpha_Factory.py")

with col2:
    if st.button("📈 Live Alpha Execution Lab", key="lab", use_container_width=True):
        st.switch_page("pages/07_Live_Alpha_Execution_Lab.py")
    if st.button("👥 ShadowCrowd Oracle", key="sc", use_container_width=True):
        st.switch_page("pages/01_ShadowCrowd_Oracle.py")

col3, col4 = st.columns(2)

with col3:
    if st.button("🌌 Financial Omniverse", key="omni", use_container_width=True):
        st.switch_page("pages/03_Financial_Omniverse.py")

with col4:
    if st.button("💰 Impact Dashboard", key="impact", use_container_width=True):
        st.switch_page("pages/06_Impact_Dashboard.py")

st.divider()
st.caption("Real causal hypotheses • Real multi-factor evolution • Real out-of-sample results")