import streamlit as st
from core.evo_factory import evolve_new_alpha
from core.registry import get_top_alphas

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
