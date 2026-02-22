import os
import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import numpy as np
import hashlib
import json
from pathlib import Path

# Cache directory setup
CACHE_DIR = Path(".hypothesis_cache")
CACHE_DIR.mkdir(exist_ok=True)

def get_cache_key(assets):
    """Generate unique cache key for asset set"""
    return hashlib.md5(json.dumps(sorted(assets)).encode()).hexdigest()

def get_cached_hypotheses(assets):
    """Retrieve cached hypotheses if available"""
    cache_file = CACHE_DIR / f"{get_cache_key(assets)}.json"
    if cache_file.exists():
        with open(cache_file, "r") as f:
            return json.load(f)
    return None

def cache_hypotheses(assets, hypotheses):
    """Cache generated hypotheses"""
    cache_file = CACHE_DIR / f"{get_cache_key(assets)}.json"
    with open(cache_file, "w") as f:
        json.dump(hypotheses, f)

# Lazy Groq client
_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
        if key:
            try:
                from groq import Groq
                _groq_client = Groq(api_key=key)
                st.success("✅ Groq client initialized successfully")
            except Exception as e:
                st.error(f"Groq init error: {e}")
                return None
    return _groq_client

def swarm_generate_hypotheses(returns):
    assets = list(returns.columns)
    
    # Check cache first
    cached = get_cached_hypotheses(assets)
    if cached:
        st.info("💾 Using cached hypotheses")
        return cached
    
    client = get_groq_client()

    prompt = f"""You are a swarm of 5 elite quant agents with distinct specialties:
1. Macro Strategist: Focuses on economic indicators, interest rates, and geopolitical events
2. Volatility Trader: Specializes in options flows, gamma exposure, and volatility regimes
3. Microstructure Expert: Analyzes order flow, dark pools, and market fragmentation
4. Data Scientist: Identifies alternative data signals and ML patterns
5. Crypto/Native: Focuses on blockchain flows, on-chain metrics, and crypto-specific dynamics

Generate 5 distinct, novel multi-factor causal hypotheses for trading alphas using these assets: {assets}.
Each hypothesis must suggest specific factors and how they causally drive returns.
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
            result = [h.strip() for h in hypotheses if h.strip() and h.startswith("Agent")]
            cache_hypotheses(assets, result)
            return result
        except Exception as e:
            st.warning(f"Groq API call failed: {e}")

    st.warning("Groq not available — using fallback hypotheses")
    result = [
        f"Agent 1: Satellite activity + low volatility regime in {np.random.choice(assets)} causally drives strong returns",
        f"Agent 2: Dark-pool flow anomalies + gamma skew predicts regime shift in {np.random.choice(assets)}",
        f"Agent 3: Web traffic surge + credit-card proxy leads persistent edge in {np.random.choice(assets)}",
        f"Agent 4: Order-flow signature + ETF creation/redemption anomalies in {np.random.choice(assets)}",
        f"Agent 5: Volatility skew cluster + shipping data causally drives {np.random.choice(assets)}"
    ]
    cache_hypotheses(assets, result)
    return result

def build_causal_dag(returns):
    G = nx.DiGraph()
    for col in returns.columns:
        G.add_node(col, metrics={'persistence': 0.0, 'influence': 0.0})
    
    edge_metrics = []
    for i, cause in enumerate(returns.columns):
        for effect in returns.columns[i+1:]:
            try:
                from statsmodels.tsa.stattools import grangercausalitytests
                gc = grangercausalitytests(returns[[cause, effect]], 5, verbose=False)
                pvals = [gc[l+1][0]['ssr_ftest'][1] for l in range(5)]
                min_pval = min(pvals)
                if min_pval < 0.05:
                    weight = 1 - min_pval
                    G.add_edge(cause, effect, weight=weight)
                    edge_metrics.append(weight)
                    
                    # Update node metrics
                    G.nodes[effect]['metrics']['persistence'] = max(G.nodes[effect]['metrics']['persistence'], weight)
                    G.nodes[effect]['metrics']['influence'] += weight
            except:
                pass
    
    # Normalize influence scores
    if edge_metrics:
        max_influence = max([G.nodes[n]['metrics']['influence'] for n in G.nodes])
        for node in G.nodes:
            if max_influence > 0:
                G.nodes[node]['metrics']['influence'] /= max_influence
    return G

def visualize_dag(G):
    net = Network(height="680px", width="100%", directed=True, bgcolor="#05050f", font_color="#ffffff")
    for node in G.nodes:
        metrics = G.nodes[node].get('metrics', {})
        net.add_node(node, 
                     title=f"Persistence: {metrics.get('persistence', 0.0):.2f}\nInfluence: {metrics.get('influence', 0.0):.2f}",
                     physics=True)
    
    for edge in G.edges(data=True):
        net.add_edge(edge[0], edge[1], value=edge[2].get('weight', 0.5))
    
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
