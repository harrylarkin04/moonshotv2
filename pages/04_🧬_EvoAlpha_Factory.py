import streamlit as st
from core.evo_factory import evolve_new_alpha
from core.registry import get_top_alphas

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
    font-size: 4.8rem;
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

.glass-box, .stMetric, .stDataFrame {
    background: rgba(15,15,45,0.85);
    backdrop-filter: blur(30px);
    border: 2px solid #00ff9f;
    border-radius: 28px;
    padding: 30px;
    box-shadow: 0 0 80px rgba(0,255,159,0.6), inset 0 0 40px rgba(0,255,159,0.2);
    transition: transform 0.4s ease, box-shadow 0.4s ease;
}

.glass-box:hover, .stMetric:hover, .stDataFrame:hover {
    transform: perspective(1000px) rotateX(8deg) rotateY(8deg) scale(1.02);
    box-shadow: 0 0 120px rgba(0,255,159,0.9), inset 0 0 60px rgba(0,255,159,0.4);
}

.stButton button {
    background: transparent;
    border: 2px solid #00ff9f;
    color: #fff;
    box-shadow: 0 0 25px #00ff9f;
    transition: all 0.4s ease;
    font-weight: 700;
    animation: neonflicker 1.5s infinite alternate;
}

.stButton button:hover {
    background: rgba(0,255,159,0.15);
    box-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff;
    transform: scale(1.08);
    border-color: #00b8ff;
}

@keyframes neonflicker {
    0% { opacity: 0.95; }
    100% { opacity: 1; }
}

.plotly-chart {
    border: 2px solid #00ff9f;
    border-radius: 16px;
    box-shadow: 0 0 60px rgba(0,255,159,0.5);
    transition: all 0.4s ease;
}

.plotly-chart:hover {
    box-shadow: 0 0 100px rgba(0,255,159,0.9);
    transform: scale(1.02);
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');
body {background: radial-gradient(circle at 50% 10%, #1a0033 0%, #05050f 70%); font-family: 'Roboto Mono', monospace;}
.big-title {font-family: 'Orbitron', sans-serif; font-size: 3.2rem; font-weight: 900; background: linear-gradient(90deg, #00ff9f, #00b8ff, #ff00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.neon-btn {border: 2px solid #00ff9f; color: #fff; background: transparent; box-shadow: 0 0 25px #00ff9f; transition: all 0.4s ease; font-weight: 700;}
.neon-btn:hover {background: rgba(0,255,159,0.15); box-shadow: 0 0 60px #00ff9f; transform: scale(1.05);}
</style>
""", unsafe_allow_html=True)

st.title("🧬 EvoAlpha Factory")
st.caption("Idea exhaustion + talent bottleneck + signal decay — obliterated")

st.markdown("**Problem it obliterates:** Human quants + traditional autoML run out of ideas; new alphas get arbitraged in months.")

st.markdown("**How the tool works:** Closed-loop multi-agent system: Researcher agents mine untapped data... Coder agents write... CausalForge validator... Omniverse simulator stress-tests against adversaries... Evolutionary algorithms mutate the winners... It runs 24/7...")

if st.button("🧬 EVOLVE NEW GENERATION NOW (Full Closed-Loop)", type="primary", use_container_width=True, key="evolve_factory"):
    with st.spinner("Researcher swarm → Coder agents → CausalForge → Omniverse → Liquidity integration → Quantum mutation..."):
        evolve_new_alpha()
        st.success("New regime-robust alpha born and deployed live.")

st.subheader("STRATEGY ZOO – FULLY INTEGRATED WITH ALL FIVE WEAPONS")
st.dataframe(get_top_alphas(25), use_container_width=True, hide_index=True)
st.caption("New alphas appear instantly after clicking the evolve button above")
