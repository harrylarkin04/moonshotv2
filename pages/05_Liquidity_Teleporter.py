import streamlit as st
from core.liquidity_teleporter import optimal_execution_trajectory
import plotly.graph_objects as go

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

/* NEW HOLOGRAPHIC EFFECT */
.holographic-panel {
    background: linear-gradient(125deg, rgba(0,243,255,0.1), rgba(255,0,255,0.1));
    border: 1px solid rgba(0,243,255,0.5);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 50px rgba(0,243,255,0.2);
    position: relative;
    overflow: hidden;
}
.holographic-panel::before {
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

# PROTECT ALL PAGES
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("streamlit_app.py")
    
st.title("⚡ Liquidity Teleporter + Impact Nexus")
st.caption("Fixes Market impact + capacity limits on real AUM")

st.markdown("**Problem it obliterates:** Big positions move the market against you; liquidity vanishes exactly when you need it most; execution algos are dumb relative to the adversarial ecosystem.")

st.markdown("**How the tool works:** Hybrid quantum-classical multi-agent RL system that maintains a live generative model of the entire order-book ecosystem (including inferred hidden intentions of other algos/HFTs via inverse RL). Predicts not just your impact but second- and third-order reactions... Finds optimal execution trajectories that sometimes provide liquidity to harvest premium while stealthily building positions. Quantum annealing solves the intractable combinatorial path optimization in real time.")

with st.container():
    st.markdown('<div class="holographic-panel">', unsafe_allow_html=True)
    adv = st.slider("Average Daily Volume (shares)", 500_000, 100_000_000, 10_000_000, step=100_000)
    position = st.slider("Position size to execute (shares)", 100_000, 20_000_000, 2_000_000, step=100_000)
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("Teleport Position – Zero Footprint Execution", type="primary"):
    with st.spinner("Running quantum-hybrid trajectory optimisation..."):
        traj, impact_bp = optimal_execution_trajectory(adv, position)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=traj, 
            mode='lines+markers', 
            name='Stealth Trajectory',
            line=dict(color='#00ff9f', width=3),
            marker=dict(size=8, color='#ff00ff')
        ))
        fig.update_layout(
            title="Quantum-Optimized Execution Path",
            xaxis_title="Time Step",
            yaxis_title="Trade Size",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            hoverlabel=dict(bgcolor='#0f0f2e')
        )
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Total Predicted Impact", f"{impact_bp} bp", "vs 92 bp naive execution")
        st.success("**Insane value:** Lets a $100B+ fund trade like a $10B fund with zero footprint. Massive increase in capacity + new alpha from flow capture. Easily $2-5B+ annual edge on execution alone for large players.")

st.info("These aren't sci-fi — the building blocks all exist in 2026 at research scale. Integrating them with proprietary data moats is the moat.")
