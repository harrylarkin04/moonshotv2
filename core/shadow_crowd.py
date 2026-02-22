import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import numpy as np
from core.data_fetcher import get_multi_asset_data

def build_exposure_graph():
    _, returns = get_multi_asset_data(period="1y")
    corr = returns.corr()
    G = nx.Graph()
    for col in corr.columns:
        G.add_node(col, title=col, size=35)
    for i in range(len(corr)):
        for j in range(i+1, len(corr)):
            if corr.iloc[i,j] > 0.73:
                G.add_edge(corr.columns[i], corr.columns[j], weight=corr.iloc[i,j])
    net = Network(height="640px", width="100%", bgcolor="#05050f")
    net.from_nx(G)
    net.save_graph("crowd.html")
    with open("crowd.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=640)
    return round(corr.where(corr > 0.73).mean().mean() * 100, 1)

def simulate_cascade_prob():
    data, _ = get_multi_asset_data(period="1mo")
    daily_vol = data.pct_change().std().mean() * 100
    recent_drawdown = (1 - data.iloc[-1]/data.max()).mean() * 100
    return round(min(9.9, daily_vol * recent_drawdown / 100), 1)
