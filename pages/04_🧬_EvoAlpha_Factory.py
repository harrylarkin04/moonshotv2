import streamlit as st
from core.evo_factory import evolve_new_alpha
from core.registry import get_top_alphas

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');
body {background: radial-gradient(circle at 50% 10%, #1a0033 0%, #05050f 70%); font-family: 'Roboto Mono', monospace;}
.big-title {font-family: 'Orbitron', sans-serif; font-size: 3.2rem; font-weight: 900; background: linear-gradient(90deg, #00ff9f, #00b8ff, #ff00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 30px #00ff9f;}
.glass {background: rgba(15,15,45,0.65); backdrop-filter: blur(20px); border: 1px solid rgba(0,255,159,0.4); box-shadow: 0 0 40px rgba(0,255,159,0.3); border-radius: 20px;}
</style>
""", unsafe_allow_html=True)

st.title("🧬 EvoAlpha Factory")
st.caption("Idea exhaustion + talent bottleneck + signal decay — obliterated")

st.markdown("**Problem it obliterates:** Human quants + traditional autoML run out of ideas; new alphas get arbitraged in months.")

st.markdown("**How the tool works:** Closed-loop multi-agent system: Researcher agents mine untapped data and literature for hypotheses → Coder agents write & debug strategies → CausalForge validator checks robustness → Omniverse simulator stress-tests against adversaries (simulated copycat funds) → Evolutionary algorithms (with quantum-inspired optimization) mutate the winners in a massive parallel \"strategy zoo.\" It runs 24/7, deploys live, monitors decay, and self-improves its own architecture. Human oversight is high-level only.")

if st.button("LAUNCH FULL CLOSED-LOOP EVOLUTION NOW", type="primary", use_container_width=True):
    with st.spinner("Researcher swarm → Coder agents → CausalForge validation → Omniverse stress-test → Liquidity integration → Quantum mutation..."):
        evolve_new_alpha()
        st.success("New regime-robust alpha deployed to live book – powered by all five weapons.")

st.subheader("STRATEGY ZOO – FULLY INTEGRATED WITH SHADOWCROWD + CAUSALFORGE + OMNIVERSE + LIQUIDITY TELEPORTER")
st.dataframe(get_top_alphas(25), use_container_width=True, hide_index=True)
st.caption("New alphas born live every 60 seconds – refresh to see the next generation")
