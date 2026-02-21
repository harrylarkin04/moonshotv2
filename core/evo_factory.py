import streamlit as st
from deap import base, creator, tools, algorithms
import random
import numpy as np
import logging
from concurrent.futures import ProcessPoolExecutor
from core.data_fetcher import get_train_test_data
from core.registry import save_alpha
from core.causal_engine import swarm_generate_hypotheses
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
    """Advanced backtesting with slippage and capacity modeling"""
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
    sharpe = (strat_ret.mean() / strat_ret.std() * np.sqrt(252)) if strat_ret.std() != 0 else 0
    return sharpe

def evaluate(individual):
    """Full pipeline evaluation with OOS validation"""
    try:
        is_returns, oos_returns = get_train_test_data()
        
        # In-sample training
        is_sharpe = backtest(individual, is_returns)
        
        # Full pipeline validation
        hypothesis = st.session_state.get("current_hypothesis", "AI-generated market edge")
        if not swarm_generate_hypotheses([hypothesis]):
            return 0.0,
        
        omniverse_score = run_omniverse_sims(scenario="Stress", num_sims=5000)
        crowd_risk = simulate_cascade_prob()
        
        # Out-of-sample validation
        oos_sharpe = backtest(individual, oos_returns)
        
        # Composite fitness score
        fitness = (oos_sharpe * 0.7 + omniverse_score * 0.2 + (1 - crowd_risk) * 0.1)
        
        # Persistence metric (decay factor)
        persistence = max(0, 0.95 - 0.05 * abs(is_sharpe - oos_sharpe))
        individual.persistence = persistence
        
        return fitness,
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 0.0,

def init_toolbox():
    """Initialize evolutionary operators"""
    toolbox.register("evaluate", evaluate)
    toolbox.register("select", tools.selTournament, tournsize=7)
    toolbox.register("mate", tools.cxBlend, alpha=0.8)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.2, indpb=0.3)

def parallel_evaluate(population):
    """Parallel evaluation of population"""
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        fitnesses = list(executor.map(toolbox.evaluate, population))
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit
    return population

def evolve_new_alpha(ui_context=False):
    """Massive evolutionary run with 1000+ population"""
    try:
        is_returns, _ = get_train_test_data()
        hypotheses = swarm_generate_hypotheses(is_returns)
        current_hypothesis = hypotheses[0] if hypotheses else "AI-generated market edge"
        
        if ui_context:
            st.session_state.current_hypothesis = current_hypothesis
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        init_toolbox()
        pop = toolbox.population(n=1200)
        
        # Evolutionary loop
        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        stats.register("avg", np.mean)
        stats.register("max", np.max)
        
        for gen in range(50):
            if ui_context:
                status_text.text(f"🔥 Generation {gen+1}/50 | Population: 1200")
                progress_bar.progress((gen+1)/50)
            
            # Selection and variation
            offspring = toolbox.select(pop, len(pop))
            offspring = [toolbox.clone(ind) for ind in offspring]
            
            # Crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.75:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            
            # Mutation
            for mutant in offspring:
                if random.random() < 0.45:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
            
            # Evaluate new individuals
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            invalid_ind = parallel_evaluate(invalid_ind)
            
            # Replace population
            pop[:] = offspring
            hof.update(pop)
        
        best = hof[0]
        fitness = best.fitness.values[0]
        persistence = getattr(best, 'persistence', 0.85)
        
        # Only save elite performers
        if fitness > 3.5 and persistence > 0.8:
            name = f"EvoAlpha_{random.randint(10000,99999)}"
            desc = f"{current_hypothesis} – evolved through Moonshot v3"
            save_alpha(name, desc, round(fitness, 2), round(persistence, 2))
            if ui_context:
                st.success(f"🚀 ELITE ALPHA: {name} | Sharpe {fitness:.2f} | Persistence {persistence:.2f}")
            return True
        else:
            if ui_context:
                st.warning(f"❌ Rejected alpha | Fitness {fitness:.2f} < 3.5 or Persistence {persistence:.2f} < 0.8")
            return False
            
    except Exception as e:
        logger.exception("Evolution failed")
        if ui_context:
            st.error(f"⚠️ Evolution crashed: {str(e)}")
        return False
