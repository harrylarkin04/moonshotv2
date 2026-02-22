import streamlit as st
import pandas as pd
from core.evo_factory import evolve_new_alpha

# Cyberpunk style for this page
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #120022 50%, #1a0033 100%);
    }
    .big-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00ff9f, #00b8ff, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px #00ff9f, 0 0 80px #00b8ff, 0 0 140px #ff00ff;
        animation: neonpulse 1.8s ease-in-out infinite alternate;
        text-align: center;
        margin: 20px 0;
    }
    @keyframes neonpulse {
        from { text-shadow: 0 0 30px #00ff9f, 0 0 60px #00b8ff; }
        to { text-shadow: 0 0 70px #00ff9f, 0 0 120px #00b8ff, 0 0 180px #ff00ff; }
    }
    .stButton button {
        background: transparent;
        border: 2px solid #00ff9f;
        color: white;
        box-shadow: 0 0 25px #00ff9f;
        transition: all 0.4s ease;
        font-weight: 700;
        font-size: 1.3rem;
    }
    .stButton button:hover {
        background: rgba(0,255,159,0.15);
        box-shadow: 0 0 70px #00ff9f, 0 0 120px #00b8ff;
        transform: scale(1.08);
    }
    .stDataFrame {
        background: rgba(15,15,45,0.9);
        backdrop-filter: blur(20px);
        border: 2px solid #00ff9f;
        border-radius: 16px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🔥 EVOALPHA FACTORY</p>', unsafe_allow_html=True)
st.markdown("**LLM Causal Hypotheses → Natural Selection → Multi-Factor Alphas**")

if st.button("EVOLVE NEW ALPHAS", type="primary", use_container_width=True):
    with st.spinner("Generating real causal hypotheses... Evolving multi-factor strategies..."):
        elite = evolve_new_alpha()
        st.session_state.elite_alphas = elite
        st.success(f"✅ {len(elite)} Multi-Factor Alphas Evolved & Deployed to Paper Trading")

# Show the table
if 'elite_alphas' in st.session_state and len(st.session_state.elite_alphas) > 0:
    df = pd.DataFrame(st.session_state.elite_alphas)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Click 'EVOLVE NEW ALPHAS' to generate and view results.")