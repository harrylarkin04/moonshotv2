import streamlit as st
import plotly.express as px
from core.backtester import run_real_oos_backtest

st.set_page_config(page_title="Live Alpha Execution Lab", layout="wide")

st.title("🚀 Live Alpha Execution Lab")
st.markdown("**Real OOS Backtested Performance on Historical Data**")

if 'elite_alphas' not in st.session_state or len(st.session_state.elite_alphas) == 0:
    st.warning("No alphas yet. Run evolution in EvoAlpha Factory first.")
    st.stop()

alphas = st.session_state.elite_alphas

st.success(f"✅ Running real OOS backtests on {len(alphas)} evolved alphas...")

results = []
for alpha in alphas:
    with st.spinner(f"Backtesting {alpha.get('name', 'Alpha')}..."):
        result = run_real_oos_backtest(alpha)
        results.append(result)

# Portfolio summary
df = pd.DataFrame(results)
st.dataframe(df[['name', 'sharpe', 'persistence', 'oos_return', 'max_drawdown']], use_container_width=True, hide_index=True)

# Cyberpunk Portfolio Equity Curve
st.subheader("Combined Portfolio Equity Curve (Real OOS)")
portfolio = sum(r['equity_curve'] for r in results) / len(results)
fig = px.line(x=portfolio.index, y=portfolio, title="Portfolio Equity Curve")
fig.update_traces(line_color='#00ffff', line_width=3)
fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.caption("All performance is real out-of-sample backtested on historical data with realistic slippage.")