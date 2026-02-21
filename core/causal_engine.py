import os
import streamlit as st
from groq import Groq
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import numpy as np

# Lazy Groq client - only created when first needed (prevents import crash)
_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
        if not key:
            return None
        _groq_client = Groq(api_key=key)
    return _groq_client

def swarm_generate_hypotheses(returns):
    client = get_groq_client()
    assets = list(returns.columns)
    
    prompt = f"""You are a swarm of 5 elite quant agents.
Generate 5 distinct, novel multi-factor causal hypotheses for trading alphas using these assets: {assets}.
Each hypothesis must suggest specific factors (satellite activity, dark-pool flow, web traffic surge, volatility skew, gamma cluster, order-flow signature, credit-card proxy, shipping data, etc.) and how they causally drive returns.
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

    # Fallback when no key or error
    st.info("Using fallback hypotheses (Groq key not detected or rate limited)")
    return [
        f"Agent 1: Satellite activity + low volatility regime in {np.random.choice(assets)} causally drives strong returns",
        f"Agent 2: Dark-pool flow anomalies + gamma skew predicts regime shift in {np.random.choice(assets)}",
        f"Agent 3: Web traffic surge + credit-card proxy leads persistent edge in {np.random.choice(assets)}",
        f"Agent 4: Order-flow signature + ETF creation/redemption anomalies in {np.random.choice(assets)}",
        f"Agent 5: Volatility skew cluster + shipping data causally drives {np.random.choice(assets)}"
    ]

# Keep your other functions (copy them from your previous version)
def build_causal_dag(returns):
    G = nx.DiGraph()
    for col in returns.columns:
        G.add_node(col)
    for i, cause in enumerate(returns.columns):
        for effect in returns.columns[i+1:]:
            try:
                gc = grangercausalitytests(returns[[cause, effect]], 5, verbose=False)
                pvals = [gc[l+1][0]['ssr_ftest'][1] for l in range(5)]
                if min(pvals) < 0.05:
                    G.add_edge(cause, effect, weight=1 - min(pvals))
            except:
                pass
    return G

def visualize_dag(G):
    net = Network(height="680px", width="100%", directed=True, bgcolor="#05050f", font_color="#ffffff")
    net.from_nx(G)
    net.save_graph("dag.html")
    with open("dag.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=680)

def counterfactual_sim(returns, shock_asset, shock_size, steps=120):
    coef = np.corrcoef(returns[shock_asset].values[:-1], returns.iloc[1:].mean(axis=1))[0,1]
    sim = returns.iloc[-steps:].copy()
    sim[shock_asset] += shock_size
    for col in sim.columns:
        if col != shock_asset:
            sim[col] += coef * shock_size * 0.65
    return (sim.cumsum() + 100)
