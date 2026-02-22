import streamlit as st
from core.evo_factory import evolve_new_alpha

st.title("🔥 EvoAlpha Factory")
st.markdown("**Real LLM causal hypotheses → Multi-factor evolution**")

if st.button("🚀 EVOLVE NEW ALPHAS", type="primary", use_container_width=True):
    with st.spinner("LLM generating causal hypotheses... Evolving multi-factor strategies..."):
        elite = evolve_new_alpha()
        st.session_state.elite_alphas = elite
        st.success(f"✅ {len(elite)} Multi-Factor Alphas Evolved")

# Show the table
if 'elite_alphas' in st.session_state and len(st.session_state.elite_alphas) > 0:
    df = pd.DataFrame(st.session_state.elite_alphas)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Run evolution to generate alphas")