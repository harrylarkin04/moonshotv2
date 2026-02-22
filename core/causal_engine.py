import streamlit as st
from openai import OpenAI
import os

# Robust OpenRouter setup
api_key = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key or "demo-key"
)

def swarm_generate_hypotheses(num=5):
    return ["Causal hypothesis " + str(i+1) for i in range(num)]

def build_causal_dag(hypotheses):
    st.info("Causal DAG built (demo version)")
    return "demo_dag"

def visualize_dag(dag):
    st.success("Neural Causal DAG visualized (demo)")

def counterfactual_sim(dag, variable, shock):
    return f"What if {variable} shocked by {shock}? (demo result)"