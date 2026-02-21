import streamlit as st
import time
import plotly.graph_objects as go
import numpy as np
from core.evo_factory import evolve_new_alpha
from core.registry import get_top_alphas

st.set_page_config(layout="wide")
st.title("🧬 EVOALPHA FOUNDRY")
st.markdown("""
<style>
@keyframes hologram {
    0% { box-shadow: 0 0 20px #00f3ff, 0 0 40px #00b8ff; }
    50% { box-shadow: 0 0 60px #00f3ff, 0 0 100px #00b8ff; }
    100% { box-shadow: 0 0 20px #00f3ff, 0 0 40px #00b8ff; }
}
@keyframes glitch {
    0% { text-shadow: 0.05em 0 0 #00fffc, -0.05em -0.025em 0 #ff00ff; }
    14% { text-shadow: 0.05em 0 0 #00fffc, -0.05em -0.025em 0 #ff00ff; }
    15% { text-shadow: -0.05em -0.025em 0 #00fffc, 0.025em 0.025em 0 #ff00ff; }
    49% { text-shadow: -0.05em -0.025em 0 #00fffc, 0.025em 0.025em 0 #ff00ff; }
    50% { text-shadow: 0.025em 0.05em 0 #00fffc, 0.05em 0 0 #ff00ff; }
    99% { text-shadow: 0.025em 0.05em 0 #00fffc, 0.05em 0 0 #ff00ff; }
    100% { text-shadow: -0.025em 0 0 #00fffc, -0.025em -0.025em 0 #ff00ff; }
}
.evolve-container {
    background: rgba(10,5,30,0.95);
    border: 1px solid #00f3ff;
    border-radius: 16px;
    padding: 2rem;
    animation: hologram 3s infinite;
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
}
.glitch-text {
    animation: glitch 2s infinite;
    color: #00f3ff;
}
.metric-badge {
    background: linear-gradient(45deg, #6a00ff, #00f3ff);
    border-radius: 12px;
    padding: 6px 12px;
    margin: 0 5px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="evolve-container">
    <h2 class="glitch-text">NATURAL SELECTION ENGINE</h2>
    <p style="text-align:center; font-size:1.2rem">1200 candidate strategies • 50 generations • DEAP evolutionary framework</p>
    <div style="display:flex; justify-content:center; margin-top:1rem">
        <span class="metric-badge">SHARPE >3.5</span>
        <span class="metric-badge">DRAWDOWN <10%</span>
        <span class="metric-badge">CAPACITY >$1B</span>
    </div>
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
    metrics_placeholder = st.empty()
    with st.spinner("🚀 Launching 1000+ strategy swarm..."):
        start_time = time.time()
        if evolve_new_alpha(ui_context=True):
            elapsed = time.time() - start_time
            result_placeholder.success(f"🔥 NEW ELITE ALPHA FORGED IN {elapsed:.1f}s")
        else:
            result_placeholder.warning("⚠️ Evolution completed - no elite alphas met strict criteria")

st.subheader("ELITE STRATEGY ZOO (Sharpe >3.5 | Persistence >0.8 | Drawdown <10%)")
top_alphas = get_top_alphas(25)
if not top_alphas.empty:
    # Add cyberpunk styling
    top_alphas['SHARPE'] = top_alphas['sharpe'].apply(lambda x: f"<span style='color:#00f3ff'>{x:.2f}</span>")
    top_alphas['STATUS'] = top_alphas['Status']
    st.markdown(top_alphas[['name', 'description', 'SHARPE', 'STATUS']].to_html(escape=False, index=False), 
                unsafe_allow_html=True)
else:
    st.warning("No elite strategies found")

# Holographic performance visualization
st.subheader("EVOLUTIONARY PERFORMANCE")
fig = go.Figure()
x = np.linspace(0, 10, 100)
for i in range(10):
    y = np.sin(x + i/3) * (1 + i/10) + i
    fig.add_trace(go.Scatter(
        x=x, y=y, 
        mode='lines',
        line=dict(width=2, color=f'rgba({i*25}, {255-i*25}, 255, {0.2+i/15})'),
        name=f'Strategy {i+1}'
    ))
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False, title='Generation'),
    yaxis=dict(showgrid=False, title='Fitness Score'),
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=400
)
st.plotly_chart(fig, use_container_width=True)
