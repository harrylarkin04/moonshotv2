import os
import streamlit as st
from openai import OpenAI

# Robust key loading for local + Streamlit Cloud
api_key = os.getenv("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")
if not api_key and hasattr(st, "secrets"):
    api_key = st.secrets.get("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")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key or "sk-or-v1-dummy-for-demo"  # fallback so it doesn't crash
)
