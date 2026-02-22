import streamlit as st
from openai import OpenAI

api_key = st.secrets.get("OPENROUTER_API_KEY")
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key) if api_key else None

def swarm_generate_hypotheses(num=10):
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1",
            messages=[{
                "role": "user", 
                "content": f"Generate exactly {num} short, clean, professional causal trading hypotheses. Output ONLY the list, no explanations, no numbering, no intro text. Each hypothesis must be under 70 characters."
            }],
            temperature=0.8
        )
        text = response.choices[0].message.content.strip()
        hypotheses = [line.strip() for line in text.split('\n') if line.strip()]
        return hypotheses[:num]
    except:
        # Clean demo fallback
        return [
            "FDA delays extend biotech R&D cycles",
            "Ocean freight volatility drives AGCO momentum",
            "Renewable portfolio standards boost clean energy",
            "AI capex shocks cause sector rotation",
            "Geopolitical risk mispricing in energy",
            "Dark pool accumulation signals momentum",
            "Retail options gamma creates volatility spikes",
            "Prime broker flow predicts crowding",
            "Low liquidity regimes amplify mean reversion",
            "Cross-asset correlation spikes predict crashes"
        ]