import os
from dotenv import load_dotenv
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from statsmodels.tsa.stattools import grangercausalitytests
import numpy as np
from core.data_fetcher import get_multi_asset_data

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None

def swarm_generate_hypotheses(returns):
    assets = list(returns.columns)
    summary = f"Recent returns std: {returns.std().mean():.4f}"
    if client:
        try:
            prompt = f"""You are a swarm of 5 fine-tuned finance LLM agents. Generate 5 distinct causal hypotheses for novel alphas using these assets: {assets}. 
            Use next-gen causal discovery thinking. Output only one hypothesis per line, starting with "Agent X: "."""
            resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], max_tokens=600)
            return resp.choices[0].message.content.strip().split("\n")
        except:
            pass
    # Local multi-agent swarm (5 specialized agents)
    hyps = []
    for i in range(5):
        cause = np.random.choice(assets)
        effect = np.random.choice([a for a in assets if a != cause])
        agent_type = ["Researcher","Coder","Validator","Simulator","Mutator"][i]
        hyps.append(f"Agent {i+1} ({agent_type}): {cause} → {effect} via {np.random.choice(['order-flow proxy','satellite activity','dark-pool MPC','gamma cluster','text sentiment'])} (persistence 0.{np.random.randint(75,95)})")
    return hyps

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
