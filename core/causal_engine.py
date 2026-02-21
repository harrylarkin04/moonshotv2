import os
from dotenv import load_dotenv
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from statsmodels.tsa.stattools import grangercausalitytests
import numpy as np
from core.data_fetcher import get_multi_asset_data
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def swarm_generate_hypotheses(returns):
    assets = list(returns.columns)
    summary = f"Assets: {', '.join(assets)}. Recent volatility: {returns.std().mean():.4f}"
    
    prompt = f"""You are a swarm of 5 elite finance LLM agents.
Generate 5 distinct, novel, multi-factor causal hypotheses for trading alphas using these assets: {assets}.
Each hypothesis must suggest specific factors (e.g., satellite activity, dark-pool flow, web traffic, volatility skew, order-flow signature) and how they causally affect returns.
Make them testable and specific.
Output only one hypothesis per line, starting with "Agent X: "."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=900
        )
        hypotheses = response.choices[0].message.content.strip().split("\n")
        return [h.strip() for h in hypotheses if h.strip() and h.startswith("Agent")]
    except:
        # Fallback for rate limit or error
        return [
            f"Agent 1: High {np.random.choice(assets)} satellite activity + low volatility regime causes strong returns in {np.random.choice(assets)}",
            f"Agent 2: Dark-pool flow anomalies in {np.random.choice(assets)} predict regime shift in {np.random.choice(assets)}",
            f"Agent 3: Web traffic surge + gamma skew in {np.random.choice(assets)} drives persistent edge in {np.random.choice(assets)}",
            f"Agent 4: Order-flow signature + ETF creation/redemption anomalies in {np.random.choice(assets)}",
            f"Agent 5: Credit-card spending proxy + shipping data causally leads {np.random.choice(assets)} returns"
        ]

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
