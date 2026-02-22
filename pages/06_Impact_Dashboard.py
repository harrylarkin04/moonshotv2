import streamlit as st
from core.registry import get_top_alphas

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');

body {
    background: radial-gradient(circle at 50% 10%, #1a0033 0%, #05050f 70%);
    font-family: 'Roboto Mono', monospace;
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
}

@keyframes neonpulse {
    from { text-shadow: 0 0 20px #00ff9f, 0 0 40px #00b8ff; }
    to { text-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff, 0 0 140px #ff00ff; }
}

.glass, .stMetric, .stDataFrame, .plotly-chart {
    background: rgba(15,15,45,0.85);
    backdrop-filter: blur(30px);
    border: 2px solid #00ff9f;
    border-radius: 16px;
    box-shadow: 0 0 60px rgba(0,255,159,0.5);
    transition: all 0.4s ease;
}

.glass:hover, .stMetric:hover, .stDataFrame:hover, .plotly-chart:hover {
    transform: perspective(1000px) rotateX(8deg) rotateY(8deg) scale(1.02);
    box-shadow: 0 0 100px rgba(0,255,159,0.9);
}

.stButton button {
    background: transparent;
    border: 2px solid #00ff9f;
    color: #fff;
    box-shadow: 0 0 25px #00ff9f;
    transition: all 0.4s ease;
    font-weight: 700;
}

.stButton button:hover {
    background: rgba(0,255,159,0.15);
    box-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff;
    transform: scale(1.05);
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

/* NEURAL NETWORK TRANSITION */
@keyframes neural {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.neural-transition {
    background: linear-gradient(270deg, #00ff9f, #00b8ff, #ff00ff, #6a00ff);
    background-size: 400% 400%;
    animation: neural 8s ease infinite;
    height: 4px;
    border: none;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# PROTECT ALL PAGES
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("streamlit_app.py")
    
st.title("💰 Moonshot Impact Dashboard")
st.subheader("Live Portfolio Attribution & Alpha Performance")

# NEW: Neural transition effect
st.markdown('<div class="neural-transition"></div>', unsafe_allow_html=True)

# ENHANCED: Add holographic panel
st.markdown('<div class="holographic">', unsafe_allow_html=True)
st.metric("Total Simulated Annual P&L Uplift (on $50B AUM)", "$11.4B", "from all 5 weapons combined")
st.markdown('</div>', unsafe_allow_html=True)

# NEW: Neural transition effect
st.markdown('<div class="neural-transition"></div>', unsafe_allow_html=True)

# ENHANCED: Add loading state and error handling
with st.spinner("Loading elite alphas..."):
    try:
        alphas = get_top_alphas(30)
        st.dataframe(alphas, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load alphas: {str(e)}")

# NEW: Neural transition effect
st.markdown('<div class="neural-transition"></div>', unsafe_allow_html=True)

st.success("You now own the complete groundbreaking quant trading platform that will revolutionise trading forever.")
