# ... (keep all existing imports except groq)
from deap import base, creator, tools, algorithms
import random
import numpy as np
import pandas as pd
import logging
import json
import math
from scipy.spatial.distance import euclidean, pdist, squareform, mahalanobis
from scipy.linalg import inv
from concurrent.futures import ProcessPoolExecutor
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.neural_network import MLPRegressor
from sklearn.decomposition import PCA
from core.data_fetcher import get_train_test_data
from core.registry import save_alpha
from core.causal_engine import swarm_generate_hypotheses, build_causal_dag, counterfactual_sim
from core.omniverse import run_omniverse_sims
from core.shadow_crowd import simulate_cascade_prob
from core.liquidity_teleporter import optimal_execution_trajectory

# Clean creator namespace before creation
for cls in ['FitnessMax', 'Individual']:
    if cls in creator.__dict__:
        del creator.__dict__[cls]

creator.create("FitnessMax", base.Fitness, weights=(1.0, 0.5, -0.2, 0.3, 0.4, 0.2, 0.3))
creator.create("Individual", list, fitness=creator.FitnessMax)

# ... (keep all existing code except Groq references)
# Removed all Groq-related code
