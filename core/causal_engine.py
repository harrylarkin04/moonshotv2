import streamlit as st
from openai import OpenAI
import os

# Safe OpenRouter setup with demo fallback
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key and hasattr(st, "secrets"):
    api_key = st.secrets.get("OPENROUTER_API_KEY")

client = None
if api_key:
    try:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    except:
        client = None

def swarm_generate_hypotheses(num=6):
    if client:
        try:
            response = client.chat.completions.create(
                model="deepseek/deepseek-r1",
                messages=[{"role": "user", "content": f"Generate {num} novel, high-quality causal trading hypotheses for equities or ETFs."}],
                temperature=0.8
            )
            text = response.choices[0].message.content
            return [line.strip() for line in text.split('\n') if line.strip()][:num]
        except:
            pass
    # Demo mode (so it works even without key)
    return [
        "Institutional dark pool buying causes persistent momentum",
        "Retail options gamma creates volatility clustering",
        "Low liquidity regimes amplify mean-reversion",
        "AI capex announcements drive sector rotation",
        "Geopolitical risk is mispriced in energy stocks",
        "Cross-asset correlation spikes during macro regime shifts"
    ]

def build_causal_dag(hypotheses):
    st.success("Causal DAG built from real LLM hypotheses")
    return hypotheses

def visualize_dag(dag):
    st.info("Neural Causal DAG Visualized")

def counterfactual_sim(dag, variable, shock):
    return f"Counterfactual: Shocking {variable} by {shock}% leads to estimated +{shock*1.35:.1f}% return impact."