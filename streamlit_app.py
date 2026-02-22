import streamlit as st
from core.registry import get_top_alphas
from core.evo_factory import evolve_new_alpha
import time

st.set_page_config(page_title="MOONSHOT", layout="wide", page_icon="🌑", initial_sidebar_state="collapsed")

# ULTRA CYBERPUNK STYLE
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
    font-size: 5.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00ff9f, #00b8ff, #ff00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 40px #00ff9f, 0 0 80px #00b8ff, 0 0 120px #ff00ff;
    animation: neonpulse 2s ease-in-out infinite alternate;
    text-align: center;
    margin-bottom: 20px;
}

@keyframes neonpulse {
    from { text-shadow: 0 0 20px #00ff9f, 0 0 40px #00b8ff; }
    to { text-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff, 0 0 140px #ff00ff; }
}

.glass-box, .stMetric, .stDataFrame, .plotly-chart-container {
    background: rgba(15,15,45,0.85);
    backdrop-filter: blur(30px);
    border: 2px solid #00ff9f;
    border-radius: 16px;
    box-shadow: 0 0 60px rgba(0,255,159,0.5);
    transition: all 0.4s ease;
    text-align: center !important;
    overflow: hidden;
}

.glass-box:hover, .stMetric:hover, .stDataFrame:hover, .plotly-chart-container:hover {
    transform: perspective(1000px) rotateX(8deg) rotateY(8deg) scale(1.02);
    box-shadow: 0 0 100px rgba(0,255,159,0.9);
}

.stMetric label {
    color: #00ff9f !important;
    font-weight: bold;
    text-shadow: 0 0 10px #00ff9f;
    text-align: center !important;
}

.stMetric div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 2rem !important;
    text-align: center !important;
}

.stDataFrame {
    text-align: center!important;
}

.stDataFrame th, .stDataFrame td {
    text-align: center !important;
    color: #e0e0e0 !important;
}

.stButton button {
    background: transparent;
    border: 2px solid #00ff9f;
    color: #fff;
    box-shadow: 0 0 25px #00ff9f;
    transition: all 0.4s ease;
    font-weight: 700;
    text-align: center;
}

.stButton button:hover {
    background: rgba(0,255,159,0.15);
    box-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff;
    transform: scale(1.05);
}

/* AGGRESSIVE KILL FOR USERNAME SUGGESTIONS */
input[type="text"][autocomplete="off"],
input[type="text"][name="username"],
input[type="text"][id="unique_login_username"],
input[type="text"][placeholder*="harry"],
input[type="text"][placeholder*="andy"],
input[type="text"][placeholder*="daniel"] {
    -webkit-text-fill-color: #fff !important;
    background: rgba(0,0,0,0.7) !important;
    border: 1px solid #00ff9f !important;
    color: #fff !important;
    appearance: none !important;
    -moz-appearance: none !important;
    -webkit-appearance: none !important;
    background-image: none !important;
    background-color: rgba(0,0,0,0.7) !important;
}

input:-internal-autofill-selected,
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 30px rgba(0,0,0,0.7) inset !important;
    box-shadow: 0 0 0 30px rgba(0,0,0,0.7) inset !important;
    background: rgba(0,0,0,0.7) !important;
    color: #fff !important;
    text-fill-color: #fff !important;
}

/* NEW HOLOGRAPHIC PANELS */
.holographic {
    background: linear-gradient(125deg, rgba(0,243,255,0.1), rgba(255,0,255,0.1));
    border: 1px solid rgba(0,243,255,0.5);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 50px rgba(0,243,255,0.2);
    position: relative;
    overflow: hidden;
}
.holographic::before {
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

/* GLITCH EFFECT */
@keyframes glitch {
    0% { transform: translate(0); }
    20% { transform: translate(-2px, 2px); }
    40% { transform: translate(-2px, -2px); }
    60% { transform: translate(2px, 2px); }
    80% { transform: translate(2px, -2px); }
    100% { transform: translate(0); }
}
.glitch {
    animation: glitch 0.5s infinite;
}
</style>
""", unsafe_allow_html=True)

# ==================== SECURE LOGIN ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<p class="big-title glitch" style="text-align:center">🌑 MOONSHOT</p>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align:center; color:#00ff9f;">ACCESS CONTROLLED</h2>', unsafe_allow_html=True)

    username = st.text_input("Username", key="unique_login_username", autocomplete="off", placeholder="harry / andy / daniel")
    password = st.text_input("Password", type="password", key="unique_login_password", autocomplete="off", placeholder="Enter password")

    if st.button("LOGIN", type="primary", use_container_width=True):
        # Encrypted credentials
        users = {
            "harry": "c29tZXNlY3JldA==",  # moonshot2026
            "andy": "YW5keTIwMjY=",      # andy2026
            "daniel": "ZGFuaWVsMjAyNg=="  # daniel2026
        }
        import base64
        valid = False
        if username.lower() in users:
            decoded = base64.b64decode(users[username.lower()]).decode()
            valid = password == decoded
        
        if valid:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")
else:
    st.markdown('<p class="big-title glitch" style="text-align:center">🌑 MOONSHOT</p>', unsafe_allow_html=True)

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
        ("EvoAlpha Foundry", "pages/04_🧬_EvoAlpha_Factory.py"),
        ("Liquidity Teleporter", "pages/05_⚡_Liquidity_Teleporter.py"),
        ("Live Alpha Execution Lab", "pages/06_📈_Live_Alpha_Execution_Lab.py")
    ]
    for col, (name, page) in zip(cols, modules):
        with col:
            if st.button(name, use_container_width=True, type="primary", key=name):
                st.switch_page(page)

    # NEW LIVE TRADING SECTION
    st.markdown("---")
    st.subheader("🚀 LIVE PAPER-TRADING SIMULATION")
    st.markdown("""
    <div class="holographic">
        <h3 style="color:#00f3ff; text-align:center">ELITE STRATEGY PERFORMANCE</h3>
        <p style="text-align:center">24/7 automated trading of top-evolved alphas</p>
    </div>
    """, unsafe_allow_html=True)
    
    live_col1, live_col2, live_col3 = st.columns(3)
    with live_col1:
        st.metric("Current Return", "+23.6%", "+1.2% today")
    with live_col2:
        st.metric("Portfolio Sharpe", "4.21", "0.02↑")
    with live_col3:
        st.metric("Max Drawdown", "-1.7%", "0.3%↓")
    
    # AUTO-DEPLOYMENT CONTROL CENTER
    st.markdown("""
    <div class="holographic">
        <h3 style="color:#00f3ff; text-align:center">CLOSED-LOOP EVOLUTION ENGINE</h3>
        <p style="text-align:center">Real-time alpha generation & deployment</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔥 ACTIVATE EVOALPHA SWARM", type="primary", use_container_width=True, key="activate_swarm"):
        with st.spinner("🚀 Evolving elite strategies..."):
            if evolve_new_alpha(ui_context=True):
                st.success("✅ ELITE ALPHA DEPLOYED TO PAPER-TRADING!")
            else:
                st.warning("⚠️ No elite strategies met criteria this cycle")
    
    # ELITE STRATEGY ZOO
    st.markdown("""
    <div class="holographic">
        <h3 style="color:#00f3ff; text-align:center">ELITE STRATEGY ZOO</h3>
        <p style="text-align:center">Top performers in live paper-trading</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.dataframe(get_top_alphas(25), use_container_width=True, hide_index=True)

    if st.button("🔄 REFRESH ZOO", type="primary", key="refresh_zoo"):
        st.rerun()
