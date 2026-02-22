import streamlit as st
import numpy as np
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.registry import get_top_alphas
from core.data_fetcher import get_multi_asset_data

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');
body { 
    background: radial-gradient(circle at 50% 10%, #1a0033 0%, #05050f 70%); 
    font-family: 'Roboto Mono', monospace; 
}
.glass-panel {
    background: rgba(15,15,45,0.85);
    backdrop-filter: blur(30px);
    border: 2px solid #00ff9f;
    border-radius: 16px;
    box-shadow: 0 0 60px rgba(0,255,159,0.5);
    transition: all 0.4s ease;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}
.glass-panel:hover {
    transform: perspective(1000px) rotateX(8deg) rotateY(8deg) scale(1.02);
    box-shadow: 0 0 100px rgba(0,255,159,0.9);
}
.metric-card {
    background: rgba(10,5,30,0.95);
    border: 1px solid rgba(0,243,255,0.5);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    transition: all 0.3s ease;
}
.metric-card:hover {
    transform: scale(1.05);
    box-shadow: 0 0 40px rgba(0,243,255,0.3);
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00ff9f, #00b8ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-label {
    font-size: 0.9rem;
    color: #00f3ff;
}
@keyframes hologram-pulse {
    0% { box-shadow: 0 0 20px #00f3ff, 0 0 40px #00b8ff; }
    50% { box-shadow: 0 0 60px #00f3ff, 0 0 100px #00b8ff; }
    100% { box-shadow: 0 0 20px #00f3ff, 0 0 40px #00b8ff; }
}
.holo-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #00f3ff, transparent);
    margin: 1.5rem 0;
    animation: hologram-pulse 3s infinite;
}
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("streamlit_app.py")

st.title("📈 Live Alpha Execution Lab")
st.caption("Real-time backtesting with slippage and transaction costs")

# IMPROVEMENT: Add loading spinner
with st.spinner("Fetching elite alphas..."):
    try:
        alphas = get_top_alphas(10)
    except Exception as e:
        st.error(f"Failed to load alphas: {str(e)}")
        st.stop()

if alphas.empty:
    st.warning("No elite alphas found. Run evolution first.")
    st.stop()

def generate_performance_charts(returns):
    """Generate interactive performance charts"""
    # Calculate performance metrics
    equity = (1 + returns).cumprod()
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add equity curve
    fig.add_trace(
        go.Scatter(x=returns.index, y=equity, name="Equity", line=dict(color='#00ff9f')),
        secondary_y=False,
    )
    
    # Add drawdown
    fig.add_trace(
        go.Scatter(x=returns.index, y=drawdown, name="Drawdown", line=dict(color='#ff00ff')),
        secondary_y=True,
    )
    
    # Add markers for max drawdown
    max_dd_idx = drawdown.idxmin()
    fig.add_annotation(
        x=max_dd_idx, y=drawdown.loc[max_dd_idx],
        text=f"Max DD: {drawdown.loc[max_dd_idx]:.2%}",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=40,
        bgcolor="#ff00ff"
    )
    
    # Format figure
    fig.update_layout(
        title='Performance Analysis',
        template='plotly_dark',
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Equity", secondary_y=False)
    fig.update_yaxes(title_text="Drawdown", secondary_y=True, tickformat=".0%")
    
    return fig

for _, alpha in alphas.iterrows():
    with st.container():
        st.markdown(f"<div class='glass-panel'>", unsafe_allow_html=True)
        
        # IMPROVEMENT: Enhanced header with persistence score
        st.subheader(f"🔮 {alpha['name']}")
        st.caption(f"Persistence: {alpha.get('persistence_score', 0.0):.2f} | Diversity: {alpha.get('diversity', 0.0):.2f}")
        
        metrics = alpha.get('oos_metrics', {})
        if isinstance(metrics, str):
            try:
                metrics = json.loads(metrics)
            except:
                metrics = {}
        
        # IMPROVEMENT: Better metric display
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{:.2f}</div>
                <div class="metric-label">SHARPE</div>
            </div>
            """.format(alpha['sharpe']), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{:.2f}</div>
                <div class="metric-label">DIVERSITY</div>
            </div>
            """.format(alpha['diversity']), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{:.2f}</div>
                <div class="metric-label">PERSISTENCE</div>
            </div>
            """.format(alpha['persistence_score']), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{:.2f}</div>
                <div class="metric-label">CONSISTENCY</div>
            </div>
            """.format(alpha['consistency']), unsafe_allow_html=True)
        
        # IMPROVEMENT: OOS metrics with period info
        if metrics:
            st.markdown("<div class='holo-divider'></div>", unsafe_allow_html=True)
            st.caption(f"OOS Metrics ({metrics.get('period', 'N/A')}):")
            
            # Create expander for detailed metrics
            with st.expander("Performance Analysis & Metrics"):
                # Generate performance charts
                if 'returns' in metrics and metrics['returns']:
                    returns = pd.Series(metrics['returns'])
                    st.plotly_chart(generate_performance_charts(returns), use_container_width=True)
                
                # Show detailed metrics table
                st.subheader("Performance Metrics")
                metric_data = {
                    "Metric": ["Sharpe Ratio", "Calmar Ratio", "Max Drawdown", 
                               "Win Rate", "Profit Factor", "Sortino Ratio"],
                    "Value": [
                        metrics.get('sharpe', 0),
                        metrics.get('calmar', 0),
                        f"{metrics.get('max_drawdown', 0):.2%}",
                        f"{metrics.get('win_rate', 0):.2%}",
                        metrics.get('profit_factor', 0),
                        metrics.get('sortino', 0)
                    ]
                }
                st.table(pd.DataFrame(metric_data))
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")  # Add spacing
