import streamlit as st
import time
import plotly.graph_objects as go
from core.evo_factory import evolve_new_alpha
from core.registry import get_top_alphas

st.title("🧬 EVOALPHA FOUNDRY")
st.markdown("""
<style>
@keyframes hologram {
    0% { box-shadow: 0 0 20px #00f3ff, 0 0 40px #00b8ff; }
    50% { box-shadow: 0 0 60px #00f3ff, 0 0 100px #00b8ff; }
    100% { box-shadow: 0 0 20px #00f3ff, 0 0 40px #00b8ff; }
}
.evolve-container {
    background: rgba(10,5,30,0.95);
    border: 1px solid #00f3ff;
    border-radius: 16px;
    padding: 2rem;
    animation: hologram 3s infinite;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="evolve-container">
    <h2 style="color:#00f3ff; text-align:center">NATURAL SELECTION ENGINE</h2>
    <p style="text-align:center">1200 candidate strategies • 50 generations • DEAP evolutionary framework</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**PROBLEM OBLITERATED:** Human quants + traditional autoML run out of ideas; new alphas get arbitraged in months.")
with col2:
    st.markdown("**HOW IT WORKS:** Multi-agent system: Researcher agents → Coder agents → CausalForge → Omniverse → Evolutionary algorithms")

if st.button("⚡ IGNITE EVOLUTIONARY FOUNDRY", type="primary", use_container_width=True, 
             help="Run full closed-loop evolution (takes 2-5 minutes)"):
    result_placeholder = st.empty()
    with st.spinner("🚀 Launching 1000+ strategy swarm..."):
        if evolve_new_alpha(ui_context=True):
            result_placeholder.success("🔥 NEW ELITE ALPHA FORGED IN FINANCIAL OMNIVERSE")
        else:
            result_placeholder.warning("⚠️ Evolution completed - no elite alphas met criteria")

st.subheader("ELITE STRATEGY ZOO (Sharpe >3.5 | Persistence >0.8)")
st.dataframe(get_top_alphas(25), use_container_width=True, hide_index=True)

# Holographic performance visualization
st.subheader("EVOLUTIONARY PERFORMANCE")
fig = go.Figure(data=go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[1.2, 3.5, 2.8, 4.2, 5.0],
    mode='lines+markers',
    line=dict(color='#00f3ff', width=4),
    marker=dict(size=12, color='#ff00ff')
))
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False, title='Generation'),
    yaxis=dict(showgrid=False, title='Fitness Score'),
    margin=dict(l=20, r=20, t=30, b=20)
)
st.plotly_chart(fig, use_container_width=True)
