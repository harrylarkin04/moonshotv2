import os
import streamlit as st
from groq import Groq
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import numpy as np

# Lazy client initialization (works on both local and Streamlit Cloud)
def get_groq_client():
    # Streamlit Cloud uses st.secrets
    key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not key:
        return None
    return Groq(api_key=key)

client = None  # Will be initialized when first needed

def swarm_generate_hypotheses(returns):
    global client
    if client is None:
        client = get_groq_client()
    
    assets = list(returns.columns)
    prompt = f"""You are a swarm of 5 elite quant agents.
Generate 5 distinct, novel multi-factor causal hypotheses for trading alphas using these assets: {assets}.
Each hypothesis must suggest specific factors (satellite activity, dark-pool flow, web traffic, volatility skew, gamma cluster, order-flow, credit-card proxy, etc.) and how they causally drive returns.
Make them concrete and testable.
Output only one hypothesis per line, starting with "Agent X: "."""

    if client:
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=900
            )
            hypotheses = response.choices[0].message.content.strip().split("\n")
            return [h.strip() for h in hypotheses if h.strip() and h.startswith("Agent")]
        except:
            pass

    # Fallback when no key or rate limit
    st.warning("⚠️ No Groq API key detected. Using fallback hypotheses.")
    return [
        f"Agent 1: Satellite activity + low volatility regime in {np.random.choice(assets)} causally drives strong returns",
        f"Agent 2: Dark-pool flow anomalies + gamma skew predicts regime shift in {np.random.choice(assets)}",
        f"Agent 3: Web traffic surge + credit-card proxy leads persistent edge in {np.random.choice(assets)}",
        f"Agent 4: Order-flow signature + ETF creation/redemption anomalies in {np.random.choice(assets)}",
        f"Agent 5: Volatility skew cluster + shipping data causally drives {np.random.choice(assets)}"
    ]

# Keep your existing functions (build_causal_dag, visualize_dag, counterfactual_sim)
# Paste them here from your previous version if needed
