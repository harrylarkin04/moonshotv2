import numpy as np
import pandas as pd
import logging
import json
import math
from deap import base, creator,tools,algorithms
import random
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

# Clean creator namespace safely
if hasattr(creator, 'FitnessMax'):
    del creator.FitnessMax
if hasattr(creator, 'Individual'):
    del creator.Individual

creator.create("FitnessMax", base.Fitness, weights=(1.0, 0.5, -0.2, 0.3, 0.4, 0.2, 0.3))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, -1, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=50)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(individual):
    # Dummy implementation to avoid crash
    sharpe = 1.0
    persistence = 0.5
    diversity = 0.3
    consistency = 0.7
    novelty = 0.2
    complexity = 0.4
    return (sharpe, persistence, diversity, consistency, novelty, complexity, 0.5)

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxBlend, alpha=0.3)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.1)
toolbox.register("select", tools.selNSGA2)

logger = logging.getLogger('evolution')
logger.setLevel(logging.DEBUG)

def evolve_new_alpha(ui_context=True):
    # Dummy implementation to avoid crash
    return None
