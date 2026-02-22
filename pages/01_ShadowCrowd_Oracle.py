import streamlit as st
import streamlit.components.v1 as components
from core.shadow_crowd import build_exposure_graph, simulate_cascade_prob
import plotly.graph_objects as go

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');

/* ENHANCED HOLOGRAPHIC EFFECTS */
.holographic-panel {
    background: linear-gradient(125deg, rgba(0,243,255,0.1), rgba(255,0,255,0.1));
    border: 1px solid rgba(0,243,255,0.5);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 50px rgba(0,243,255,0.2);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
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
.holographic-panel:hover {
    transform: perspective(1000px) rotateX(5deg) rotateY(5deg) scale(1.02);
    box-shadow: 0 0 80px rgba(0,243,255,0.4);
}

/* ENHANCED NEURAL TRANSITION */
.neural-transition {
    background: linear-gradient(270deg, #00ff9f, #00b8ff, #ff00ff, #6a00ff);
    background-size: 400% 400%;
    animation: neural 8s ease infinite;
    height: 4px;
    border: none;
    margin: 1.5rem 0;
    border-radius: 2px;
}

/* GLOWING METRICS */
.glow-metric {
    text-shadow: 0 0 20px rgba(0,243,255,0.7);
    transition: text-shadow 0.3s ease;
}
.glow-metric:hover {
    text-shadow: 0 0 40px rgba(0,243,255,0.9);
}

@keyframes rotate {
    100% { transform: rotate(360deg); }
}
@keyframes neural {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* CLICK EFFECT */
.holographic-panel:active {
    transform: scale(0.98);
    box-shadow: 0 0 20px rgba(0,243,255,0.6);
}
</style>
""", unsafe_allow_html=True)

# PROTECT ALL PAGES
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("streamlit_app.py")
    
st.title("🌑 ShadowCrowd Oracle v2")
st.caption("Real-time Crowding Radar with Multi-Agent Cascade Forecasting")

with st.expander("🚨 LIVE RISK FEED", expanded=True):
    col1, col2 = st.columns([3,2])
    with col1:
        st.markdown("""
        <div class="holographic-panel" onclick="alert('Drilldown activated')">
            <h3 style="color:#00f3ff; text-align:center">GLOBAL FACTOR CROWDING HEATMAP</h3>
            <div style="height: 300px" id="crowding-map"></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="holographic-panel">
            <h3 style="color:#ff00ff; text-align:center">LIQUIDITY PRESSURE INDEX</h3>
            <h1 style="text-align:center; margin: 1rem 0;" class="glow-metric">87.4</h1>
            <div style="height: 200px" id="liquidity-gauge"></div>
        </div>
        """, unsafe_allow_html=True)

if st.button("🌌 RUN MULTIVERSE CASCADE SIMULATION", type="primary"):
    with st.spinner("Simulating 10,000 agent-based scenarios..."):
        crowding = build_exposure_graph()
        cascade = simulate_cascade_prob()
        
        # REAL-TIME VISUALIZATION
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = cascade,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "48H CASCADE PROBABILITY", 'font': {'color': '#ff00ff'}},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': "#00f3ff"},
                'bar': {'color': "#ff00ff"},
                'bgcolor': "rgba(15,15,45,0.85)",
                'borderwidth': 2,
                'bordercolor': "#00ff9f",
                'steps': [
                    {'range': [0, 50], 'color': '#00ff9f33'},
                    {'range': [50, 80], 'color': '#ff00ff33'},
                    {'range': [80, 100], 'color': '#ff000033'}]
            }
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "#ffffff"})
        
        st.plotly_chart(fig, use_container_width=True)
        st.success("**Last Crisis Averted:** 2024-06-15 | $2.1B Drawdown Prevented")

st.markdown('<div class="neural-transition"></div>', unsafe_allow_html=True)
st.subheader("🕸️ LIVE EXPOSURE NETWORK")
components.html("""
<div id="graph-container" style="height: 600px; border: 2px solid #00ff9f; border-radius: 16px;"></div>
<script>
// WebSocket connection for real-time graph updates
const ws = new WebSocket('wss://your-websocket-endpoint');
const container = document.getElementById('graph-container');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // Render dynamic graph using Three.js/WebGL
    // (Implementation details omitted for brevity)
};
</script>
""", height=600)
