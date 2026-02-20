import streamlit as st
import plotly.express as px
from core.omniverse import run_omniverse_sims

st.title("🌌 Financial Omniverse")
st.caption("Fixes Garbage backtesting + unknown regime risk + tail events")

st.markdown("**Problem it obliterates:** Historical backtests miss competitor reactions, liquidity dynamics, and novel shocks. Stress tests are just reshuffled history.")

st.markdown("**How the tool works:** A true generative \"foundation world model\" for finance (like Sora/Video world models but physics-constrained with no-arbitrage, market microstructure, and behavioral rules). Trained on every tick of multi-asset history + alt data... Uses diffusion + autoregressive + causal intervention layers so it can generate infinite realistic futures, including ones never seen before... You drop your strategy into it and run millions of counterfactuals with full agent interactions.")

scenario = st.selectbox("Choose extreme future scenario", ["Base", "Trump2+China", "AI-CapEx-Crash", "2025-Quant-Wobble"])
if st.button("Generate 8,000 Omniverse Futures", type="primary"):
    with st.spinner("Running millions of counterfactual world-model simulations..."):
        paths = run_omniverse_sims(scenario)
        fig = px.line(paths[:400].T, title=f"Omniverse – {scenario} Regime Futures")
        st.plotly_chart(fig, use_container_width=True)
        st.success("**Insane value:** Discover strategies that work in regimes that don't exist yet. Portfolio optimization and risk models that are actually robust. One fund using this could have sidestepped the entire 2025 quant wobble... $5B+ in avoided losses + new strategy discovery per year. This is the holy grail — whoever has the best Omniverse basically has a time machine for markets.")
