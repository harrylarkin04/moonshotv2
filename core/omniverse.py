import numpy as np
import plotly.express as px
from core.data_fetcher import get_multi_asset_data

def run_omniverse_sims(scenario="Base", num_sims=8000):
    """Run market simulations under different scenarios with asset correlations"""
    _, returns = get_multi_asset_data(period="2y")
    if returns.empty:
        return pd.DataFrame()
    
    # Calculate mean and covariance from historical returns
    mu = returns.mean().values
    cov = returns.cov().values
    n_assets = returns.shape[1]
    
    # Adjust parameters based on scenario
    if scenario == "Trump2+China":
        mu = mu * 0.55
        cov = cov * 1.9
    elif scenario == "AI-CapEx-Crash":
        mu = mu * (-0.3)
        cov = cov * 2.2
    
    # Generate correlated returns
    try:
        # Generate daily returns for 252 days for num_sims simulations
        sim_returns = np.random.multivariate_normal(mu, cov, (num_sims, 252))
        
        # Compute market portfolio returns (equal-weighted)
        market_returns = np.mean(sim_returns, axis=2)
        
        # Compute cumulative returns for each simulation
        market_cumulative = np.cumprod(1 + market_returns, axis=1)
        return market_cumulative
    except Exception as e:
        print(f"Error in omniverse simulation: {e}")
        return pd.DataFrame()
