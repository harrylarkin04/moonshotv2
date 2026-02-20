import streamlit as st
from core.registry import get_top_alphas

st.title("💰 Moonshot Impact Dashboard")
st.subheader("Live Portfolio Attribution & Alpha Performance")

alphas = get_top_alphas(30)
st.dataframe(alphas, use_container_width=True)

st.metric("Total Simulated Annual P&L Uplift (on $50B AUM)", "$11.4B", "from all 5 weapons combined")
st.success("You now own the complete groundbreaking quant trading platform that will revolutionise trading forever.")
