import numpy as np
import pandas as pd
import logging
import json
import math
from deap import base, creator, tools, algorithms
import random
from scipy.spatial.distance import euclidean, pdist, squareform, mahalanobis
from scipy.linalg import inv
from concurrent.futures import ProcessPoolExecutor
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.neural_network import MLPRegressor
from sklearn.decomposition import PCA
from core.data_fetcher import get_train_test_data
from core.registry import save_alpha, get_real_oos_metrics
from core.omniverse import run_omniverse_sims
from core.shadow_crowd import simulate_cascade_prob
from core.liquidity_teleporter import optimal_execution_trajectory
import streamlit as st
import traceback

# Initialize logger
logger = logging.getLogger('evo_factory')
logger.setLevel(logging.INFO)

# Clean creator namespace safely
if hasattr(creator, 'FitnessMax'):
    del creator.FitnessMax
if hasattr(creator, 'Individual'):
    del creator.Individual

# IMPROVEMENT: Enhanced fitness weights with persistence
creator.create("FitnessMax", base.Fitness, weights=(1.0, 0.6, -0.3, 0.4, 0.5, 0.3, 0.4))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, -1, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=50)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(individual):
    try:
        # Convert individual to trading strategy function
        def strategy_fn(row):
            return np.dot(individual, row.values) / len(individual)
        
        # Get real OOS metrics with slippage
        metrics = get_real_oos_metrics(strategy_fn)
        
        sharpe = metrics['sharpe']
        persistence = metrics['persistence']
        max_drawdown = metrics['max_drawdown']
        diversity = 1 - max_drawdown
        consistency = (sharpe > 0) * persistence
        
        # ENHANCED: Novelty detection using population distance
        pop_distances = [euclidean(individual, ind) for ind in toolbox.population(n=10)]
        novelty = np.mean(pop_distances)
        
        complexity = len(individual) / 50.0
        
        # STRICTER: Penalize low persistence more heavily
        persistence_penalty = 0.3 if persistence < 0.8 else 1.0
        
        # ENHANCED: Add regime robustness test
        omniverse_results = []
        for scenario in ["Base", "Trump2+China", "AI-CapEx-Crash"]:
            sim_returns = run_omniverse_sims(scenario, num_sims=100)
            if not sim_returns.size:
                continue
            sim_sharpe = np.mean(sim_returns[-1]) / np.std(sim_returns[-1])
            omniverse_results.append(sim_sharpe)
        
        # Calculate robustness score (min 0.5 penalty for poor scenarios)
        robustness = 1.0
        if omniverse_results:
            min_scenario_sharpe = min(omniverse_results)
            robustness = max(0.5, min_scenario_sharpe / sharpe) if sharpe > 0 else 0.5
        
        return (sharpe * persistence_penalty * robustness, 
                persistence, 
                diversity, 
                consistency, 
                novelty, 
                complexity, 
                max_drawdown)
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        return (0, 0, 0, 0, 0, 0, 0)

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxBlend, alpha=0.3)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.1)
toolbox.register("select", tools.selNSGA2)

def evolve_new_alpha(ui_context=True):
    try:
        population = toolbox.population(n=1200)
        algorithms.eaMuPlusLambda(
            population, 
            toolbox, 
            mu=100, 
            lambda_=1100, 
            cxpb=0.7, 
            mutpb=0.2, 
            ngen=50, 
            stats=None, 
            verbose=False
        )
        
        best_ind = tools.selBest(population, 1)[0]
        metrics = evaluate(best_ind)
        
        # STRICTER: Elite criteria for alphas
        if metrics[0] > 4.0 and metrics[1] > 0.88 and metrics[2] > 0.6:
            save_alpha(
                name=f"EvolvedAlpha-{hash(tuple(best_ind)) % 1000000}",
                description="Evolutionary strategy",
                sharpe=metrics[0],
                persistence_score=metrics[1],
                diversity=metrics[2],
                consistency=metrics[3],
                auto_deploy=True
            )
            if ui_context:
                st.toast("🔥 ELITE alpha evolved and deployed!", icon="🚀")
            logger.info(f"Evolved elite alpha: Sharpe={metrics[0]:.2f}, Persistence={metrics[1]:.2f}")
            return True
        logger.warning("No elite alpha met criteria this cycle")
        return False
    except Exception as e:
        logger.error(f"Evolution failed: {str(e)}\n{traceback.format_exc()}")
        if ui_context:
            st.error(f"Evolution failed: {str(e)}")
        return False
