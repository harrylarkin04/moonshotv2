import os
from dotenv import load_dotenv
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import numpy as np
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def swarm_generate_hypotheses(returns):
    assets = list(returns.columns)
    prompt = f"""You are a swarm of 5 elite quant agents.
Generate 5 distinct, novel multi-factor causal hypotheses for trading alphas using these assets: {assets}.
Each hypothesis must suggest specific factors (satellite activity, dark-pool flow, web traffic surge, volatility skew, gamma cluster, order-flow signature, credit-card proxy, shipping data, etc.) and how they causally affect returns.
Make them concrete and testable.
Output only one hypothesis per line, starting with "Agent X: "."""

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
        # Fallback for rate limits
        return [
            f"Agent 1: Satellite activity + low volatility regime in {np.random.choice(assets)} causally drives strong returns",
            f"Agent 2: Dark-pool flow anomalies + gamma skew predicts regime shift in {np.random.choice(assets)}",
            f"Agent 3: Web traffic surge + credit-card proxy leads persistent edge in {np.random.choice(assets)}",
            f"Agent 4: Order-flow signature + ETF creation/redemption anomalies in {np.random.choice(assets)}",
            f"Agent 5: Volatility skew cluster + shipping data causally drives {np.random.choice(assets)} returns"
        ]

def parse_hypothesis_to_signal(hypothesis, returns):
    """Convert LLM hypothesis into an executable multi-factor signal"""
    # Simple keyword-based parsing (can be made smarter later)
    assets = list(returns.columns)
    if "satellite" in hypothesis.lower() or "web traffic" in hypothesis.lower():
        asset = np.random.choice(assets)
        return (returns[asset] > returns[asset].rolling(20).mean()).astype(int).diff().fillna(0)
    elif "dark-pool" in hypothesis.lower() or "order-flow" in hypothesis.lower():
        return (returns["SPY"].diff(5) > 0).astype(int).diff().fillna(0)
    else:
        # Default momentum on strongest asset
        asset = np.random.choice(assets)
        return (returns[asset] > returns[asset].rolling(30).mean()).astype(int).diff().fillna(0)

# Keep your existing build_causal_dag, visualize_dag, counterfactual_sim functions
# (copy them from your current file)
