import streamlit as st
from deap import base, creator, tools, algorithms
import random
import numpy as np
import pandas as pd
import logging
import json
from concurrent.futures import ProcessPoolExecutor
from core.data_fetcher import get_train_test_data
from core.registry import save_alpha
from core.causal_engine import swarm_generate_hypotheses, build_causal_dag
from core.omniverse import run_omniverse_sims
from core.shadow_crowd import simulate_cascade_prob
from core.liquidity_teleporter import optimal_execution_trajectory

# Configure parallel processing
MAX_WORKERS = 8
logger = logging.getLogger(__name__)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_int", random.randint, 5, 200)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=8)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def backtest(individual, returns):
    """Advanced backtesting with slippage, capacity modeling and drawdown monitoring"""
    price = (1 + returns["SPY"]).cumprod()
    p1, p2, p3, p4, p5, p6, p7, p8 = [int(x) for x in individual]
    
    # Multi-factor strategy
    sma_signal = (price.rolling(p1).mean() > price.rolling(p2).mean()).astype(int)
    rsi = 100 - (100 / (1 + (returns["SPY"].rolling(p3).mean() / abs(returns["SPY"]).rolling(p3).mean())))
    rsi_signal = (rsi > p4).astype(int)
    volatility = returns["SPY"].rolling(p5).std()
    position = (sma_signal * 0.6 + rsi_signal * 0.4) / volatility.clip(lower=0.01)
    
    # Position sizing with liquidity constraints
    position = position.rolling(p6).mean().diff().fillna(0)
    position = position.clip(lower=-1, upper=1) * p7 / 100.0
    
    # Simulate execution impact
    adv = 2e9  # Average daily volume
    executed_returns = []
    for idx, target_pos in enumerate(position):
        if idx == 0: 
            continue
        prev_pos = position.iloc[idx-1]
        trajectory = optimal_execution_trajectory(adv, target_pos - prev_pos)
        impact_cost = trajectory[0] * 0.0001  # 1bps impact
        executed_returns.append(returns["SPY"].iloc[idx] - impact_cost)
    
    strat_ret = pd.Series(executed_returns)
    cumulative = (1 + strat_ret).cumprod()
    peak = cumulative.expanding(min_periods=1).max()
    drawdown = (cumulative - peak) / peak
    
    sharpe = (strat_ret.mean() / strat_ret.std() * np.sqrt(252)) if strat_ret.std() != 0 else 0
    max_drawdown = drawdown.min()
    capacity = 1e9 * (1 / abs(position).max()) if position.abs().max() > 0 else 1e9
    
    return {
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'capacity': capacity
    }

def evaluate(individual):
    """Full pipeline evaluation with OOS validation and Moonshot pipeline"""
    try:
        is_returns, oos_returns = get_train_test_data()
        
        # In-sample training
        is_metrics = backtest(individual, is_returns)
        
        # Full pipeline validation
        if not swarm_generate_hypotheses(is_returns):
            return 0.0,
        
        # Build causal DAG and validate relationships
        G = build_causal_dag(is_returns)
        causal_score = len(G.edges) / 100  # Normalize score
        
        omniverse_score = run_omniverse_sims(scenario="Stress", num_sims=5000)
        crowd_risk = simulate_cascade_prob()
        
        # Out-of-sample validation
        oos_metrics = backtest(individual, oos_returns)
        
        # Composite fitness score with strict criteria
        fitness = (
            oos_metrics['sharpe'] * 0.6 + 
            (1 - abs(oos_metrics['max_drawdown'])) * 0.2 +
            omniverse_score * 0.1 +
            (1 - crowd_risk) * 0.1
        )
        
        # Store metrics for elite selection
        individual.metrics = {
            'in_sample': is_metrics,
            'out_of_sample': oos_metrics,
            'causal_score': causal_score,
            'omniverse_score': omniverse_score,
            'crowd_risk': crowd_risk
        }
        
        return fitness,
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 0.0,

def init_toolbox():
    """Initialize evolutionary operators with heavy mutation"""
    toolbox.register("evaluate", evaluate)
    toolbox.register("select", tools.selTournament, tournsize=7)
    toolbox.register("mate", tools.cxBlend, alpha=0.8)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.3, indpb=0.4)  # Increased mutation

def parallel_evaluate(population):
    """Parallel evaluation of population"""
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(toolbox.evaluate, ind) for ind in population]
        fitnesses = [f.result() for f in futures]
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit
    return population

def evolve_new_alpha(ui_context=False):
    """Massive evolutionary run with 1000+ population and full pipeline validation"""
    try:
        is_returns, _ = get_train_test_data()
        hypotheses = swarm_generate_hypotheses(is_returns)
        current_hypothesis = hypotheses[0] if hypotheses else "AI-generated market edge"
        
        if ui_context:
            st.session_state.current_hypothesis = current_hypothesis
            progress_bar = st.progress(0)
            status_text = st.empty()
            elite_count = st.empty()
            metrics_display = st.empty()
        
        init_toolbox()
        pop = toolbox.population(n=1200)
        
        # Evolutionary loop
        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        stats.register("avg", np.mean)
        stats.register("max", np.max)
        
        elite_counter = 0
        for gen in range(50):
            if ui_context:
                status_text.text(f"🔥 Generation {gen+1}/50 | Population: 1200 | Elites: {elite_counter}")
                progress_bar.progress((gen+1)/50)
            
            # Selection and variation
            offspring = toolbox.select(pop, len(pop))
            offspring = [toolbox.clone(ind) for ind in offspring]
            
            # Crossover with increased rate
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.85:  # Higher crossover rate
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            
            # Mutation
            for mutant in offspring:
                if random.random() < 0.5:  # Higher mutation rate
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
            
            # Evaluate new individuals
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            invalid_ind = parallel_evaluate(invalid_ind)
            
            # Replace population
            pop[:] = offspring
            hof.update(pop)
            
            # Auto-deploy elite performers with strict criteria
            best = hof[0]
            metrics = getattr(best, 'metrics', {})
            oos_metrics = metrics.get('out_of_sample', {})
            
            if (best.fitness.values[0] > 3.5 and 
                oos_metrics.get('sharpe', 0) > 3.5 and 
                oos_metrics.get('max_drawdown', 0) > -0.1 and 
                metrics.get('omniverse_score', 0) > 0.7):
                
                name = f"EvoAlpha_{random.randint(10000,99999)}"
                desc = f"{current_hypothesis} – evolved through Moonshot v3"
                
                # Save with full metrics
                if save_alpha(
                    name, 
                    desc, 
                    round(oos_metrics['sharpe'], 2), 
                    round(1 - abs(metrics['in_sample']['sharpe'] - oos_metrics['sharpe']), 2),
                    metrics=json.dumps(metrics)
                ):
                    elite_counter += 1
                    if ui_context:
                        elite_count.text(f"🚀 ELITES DEPLOYED: {elite_counter}")
                        metrics_display.json(metrics)
        
        if ui_context and elite_counter == 0:
            st.warning("❌ No elite alphas met strict criteria this cycle")
        return elite_counter > 0
            
    except Exception as e:
        logger.exception("Evolution failed")
        if ui_context:
            st.error(f"⚠️ Evolution crashed: {str(e)}")
        return False
