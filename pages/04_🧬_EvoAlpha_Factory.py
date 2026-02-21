import streamlit as st
from core.evo_factory import evolve_new_alpha
from core.registry import get_top_alphas

st.title("🧬 EvoAlpha Factory")

st.markdown("**Problem it obliterates:** Human quants + traditional autoML run out of ideas; new alphas get arbitraged in months.")

st.markdown("**How the tool works:** Closed-loop multi-agent system: Researcher agents mine untapped data and literature for hypotheses → Coder agents write & debug strategies → CausalForge validator checks robustness → Omniverse simulator stress-tests against adversaries → Evolutionary algorithms mutate the winners.")

if st.button("🧬 EVOLVE NEW GENERATION NOW (Full Closed-Loop)", type="primary", use_container_width=True):
    with st.spinner("Running full closed-loop evolution..."):
        evolve_new_alpha()

st.subheader("Strategy Zoo")
st.dataframe(get_top_alphas(25), use_container_width=True, hide_index=True)
