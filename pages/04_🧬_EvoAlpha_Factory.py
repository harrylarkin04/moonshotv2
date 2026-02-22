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
    0% { box-shadow: 0 0 20px #00f3ff, 0 0 40px #00b8ff; }50% { box-shadow: 0 0 60px #00f3ff, 0 0 100px #00b8ff; }
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
.progress-container {
    background: rgba(0,0,0,0.3);
    border-radius: 10px;
    margin: 5px 0;
    overflow: hidden;
}
.progress-bar {
    height: 10px;
    background: linear-gradient(90deg, #6a00ff, #00f3ff);
    border-radius: 10px;
}
.diversity-panel {
    background: linear-gradient(135deg, rgba(106,0,255,0.2), rgba(0,243,255,0.2));
    border: 1px solid rgba(0,243,255,0.5);
    border-radius: 12px;
    padding: 1rem;
    margin: 1rem 0;
    box-shadow: 0 0 30px rgba(0,243,255,0.3);
}
.holographic-viz {
    background: linear-gradient(135deg, rgba(0,243,255,0.1), rgba(106,0,255,0.1));
    border: 1px solid rgba(0,243,255,0.5);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    box-shadow: 0 0 50px rgba(0,243,255,0.2);
    position: relative;
    overflow: hidden;
}
.holographic-viz::before {
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
        <span class="metric-badge">DIVERSITY >0.3</span>
        <span class="metric-badge">CONSISTENCY >0.7</span>
        <span class="metric-badge" style="background:linear-gradient(45deg, #ff00ff, #ff66ff)">NOVELTY >0.5</span>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**PROBLEM OBLITERATED:** Human quants + traditional autoML run out of ideas; new alphas get arbitraged in months.")
with col2:
    st.markdown("**HOW IT WORKS:** Multi-agent system: Researcher agents → Coder agents → CausalForge → Omniverse → Evolutionary algorithms")

# Add current hypothesis display
if 'current_hypothesis' not in st.session_state:
    st.session_state.current_hypothesis = "Market microstructure + dark pool flow anomalies"
    
st.markdown(f"""
<div class="evolve-container" style="padding:1rem; margin-top:1rem">
    <h3>ACTIVE HYPOTHESIS</h3>
    <p style="font-size:1.1rem; color:#00f3ff">🔮 {st.session_state.current_hypothesis}</p>
</div>
""", unsafe_allow_html=True)

# Add diversity info panel
st.markdown("""
<div class="diversity-panel">
    <h4 style="color:#00f3ff; text-align:center">POPULATION DIVERSITY</h4>
    <p style="text-align:center">Higher diversity = stronger evolutionary pressure</p>
    <div style="display:flex; justify-content:center; gap:1rem">
        <div class="metric-badge">LOW <0.2</div>
        <div class="metric-badge">MEDIUM 0.2-0.4</div>
        <div class="metric-badge">HIGH >0.4</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Evolution controls sidebar
with st.sidebar.expander("⚙️ EVOLUTION PARAMETERS"):
    st.session_state.pop_size = st.slider("Population Size", 500, 2000, 1200, 100)
    st.session_state.max_gens = st.slider("Max Generations", 20, 100, 50, 5)
    st.session_state.elite_rate = st.slider("Elite Rate", 0.01, 0.2, 0.05, 0.01)
    st.session_state.novelty_weight = st.slider("Novelty Weight", 0.1, 1.0, 0.4, 0.05)

# Holographic visualization placeholder
st.subheader("EVOLUTIONARY PERFORMANCE")
hologram_placeholder = st.empty()
novelty_placeholder = st.empty()

if st.button("⚡ IGNITE EVOLUTIONARY FOUNDRY", type="primary", use_container_width=True, 
             help="Run full closed-loop evolution (takes 2-5 minutes)"):
    result_placeholder = st.empty()
    metrics_placeholder = st.empty()
    with st.spinner("🚀 Launching strategy swarm..."):
        start_time = time.time()
        if evolve_new_alpha(ui_context=True):
            elapsed = time.time() - start_time
            result_placeholder.success(f"🔥 NEW ELITE ALPHA FORGED IN {elapsed:.1f}s")
        else:
            result_placeholder.warning("⚠️ Evolution completed - no elite alphas met strict criteria")

st.subheader("ELITE STRATEGY ZOO (Sharpe >3.5 | Persistence >0.8 | Drawdown <10% | Diversity >0.3 | Consistency >0.7 | Novelty >0.5)")
top_alphas = get_top_alphas(25)
if not top_alphas.empty:
    # Enhanced display with progress bars
    for _, row in top_alphas.iterrows():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**{row['name']}**")
            st.caption(row['description'])
            # Display diversity and novelty metrics
            st.markdown(f"**Diversity:** `{row.get('diversity', 0.0):.3f}`")
            st.markdown(f"**Novelty:** `{row.get('novelty', 0.0):.3f}`")
        with col2:
            # Sharpe progress
            sharpe_pct = min(row['sharpe'] / 5.0, 1.0)
            st.markdown(f"SHARPE: `{row['sharpe']:.2f}`")
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width:{sharpe_pct*100}%"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Drawdown progress
            dd_pct = min(abs(row['max_drawdown']) / 0.2, 1.0)
            st.markdown(f"DRAWDOWN: `{abs(row['max_drawdown'])*100:.1f}%`")
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width:{dd_pct*100}%; background:linear-gradient(90deg, #ff0066, #ff6600)"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Capacity progress
            cap_pct = min(row['capacity'] / 2e9, 1.0)
            st.markdown(f"CAPACITY: `${row['capacity']/1e6:.0f}M`")
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width:{cap_pct*100}%; background:linear-gradient(90deg, #00cc66, #00ff99)"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Novelty progress
            novelty_pct = min(row.get('novelty', 0.0) / 1.0, 1.0)
            st.markdown(f"NOVELTY: `{row.get('novelty', 0.0):.3f}`")
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width:{novelty_pct*100}%; background:linear-gradient(90deg, #ff00ff, #ff66ff)"></div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
else:
    st.warning("No elite strategies found")
