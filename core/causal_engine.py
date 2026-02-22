import os
import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import numpy as np
import hashlib
import json
from pathlib import Path
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Rest of causal engine functions remain unchanged
