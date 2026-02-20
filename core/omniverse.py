import numpy as np
import plotly.express as px
from core.data_fetcher import get_multi_asset_data

def run_omniverse_sims(scenario="Base", num_sims=8000):
    _, hist = get_multi_asset_data(period="3y")
    mu, sigma = hist["SPY"].mean(), hist["SPY"].std()
    if scenario == "Trump2+China":
        mu *= 0.55
        sigma *= 1.9
    elif scenario == "AI-CapEx-Crash":
        mu *= -0.3
        sigma *= 2.2
    sims = np.random.normal(mu, sigma, (num_sims, 252))
    return np.cumprod(1 + sims, axis=1)
