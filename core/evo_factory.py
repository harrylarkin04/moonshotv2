import streamlit as st
from deap import base, creator, tools, algorithms
import random
import numpy as np
import pandas as pd
import logging
import json
import math
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
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=10)  # Increased parameters
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def backtest(individual, returns):
    """Advanced backtesting with multi-asset support and walk-forward validation"""
    if len(returns.columns) < 3:
        raise ValueError("Insufficient assets for portfolio construction")
    
    # Extract parameters
    p1, p2, p3, p4, p5, p6, p7, p8, p9, p10 = [int(x) for x in individual]
    
    # Portfolio construction parameters
    asset_weights = np.array([p1, p2, p3, p4])[:len(returns.columns)]
    asset_weights = asset_weights / asset_weights.sum()
    
    # Walk-forward validation
    wf_results = []
    for i in range(0, len(returns)-p9, p10):
        chunk = returns.iloc[i:i+p9]
        if len(chunk) < 30:  # Minimum data requirement
            continue
            
        # Multi-asset strategy
        signals = pd.DataFrame()
        for col in returns.columns:
            price = (1 + returns[col]).cumprod()
            sma_signal = (price.rolling(p5).mean() > price.rolling(p6).mean()).astype(int)
            rsi = 100 - (100 / (1 + (returns[col].rolling(p7).mean() / abs(returns[col]).rolling(p7).mean())))
            rsi_signal = (rsi > p8).astype(int)
            signals[col] = (sma_signal * 0.6 + rsi_signal * 0.4)
        
        # Position sizing with liquidity constraints
        position = signals.rolling(p6).mean().diff().fillna(0)
        position = position.clip(lower=-1, upper=1) * p7 / 100.0
        
        # Portfolio weighting
        weighted_returns = (position * asset_weights).sum(axis=1)
        
        # Simulate execution impact
        strat_ret = []
        for idx in range(1, len(weighted_returns)):
            prev_pos = position.iloc[idx-1]
            curr_pos = position.iloc[idx]
            position_change = (curr_pos - prev_pos) * asset_weights
            
            # Calculate impact cost for each asset
            total_impact = 0
            for j, col in enumerate(returns.columns):
                adv = 2e9  # Average daily volume
                trajectory = optimal_execution_trajectory(adv, position_change[j])
                total_impact += trajectory[0] * 0.0001  # 1bps impact
            
            strat_ret.append(weighted_returns.iloc[idx] - total_impact)
        
        strat_ret = pd.Series(strat_ret)
        cumulative = (1 + strat_ret).cumprod()
        peak = cumulative.expanding(min_periods=1).max()
        drawdown = (cumulative - peak) / peak
        
        sharpe = (strat_ret.mean() / strat_ret.std() * np.sqrt(252)) if strat_ret.std() != 0 else 0
        max_drawdown = drawdown.min()
        capacity = 1e9 * (1 / abs(position).max().max()) if position.abs().max().max() > 0 else 1e9
        
        wf_results.append({
            'sharpe': sharpe,
            'max_drawdown': max_drawdown,
            'capacity': capacity
        })
    
    # Aggregate walk-forward results
    if not wf_results:
        return {'sharpe': 0, 'max_drawdown': 0, 'capacity': 0}
    
    avg_sharpe = np.mean([r['sharpe'] for r in wf_results])
    avg_drawdown = np.mean([r['max_drawdown'] for r in wf_results])
    avg_capacity = np.mean([r['capacity'] for r in wf_results])
    
    return {
        'sharpe': avg_sharpe,
        'max_drawdown': avg_drawdown,
        'capacity': avg_capacity
    }

def evaluate(individual):
    """Full pipeline evaluation with OOS validation and Moonshot pipeline"""
    try:
        is_returns, oos_returns = get_train_test_data()
        
        # In-sample training with walk-forward
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
        
        # Calculate overfitting penalty
        overfit_penalty = abs(is_metrics['sharpe'] - oos_metrics['sharpe']) * 0.5
        
        # Composite fitness score with strict criteria
        fitness = (
            oos_metrics['sharpe'] * 0.6 + 
            (1 - abs(oos_metrics['max_drawdown'])) * 0.2 +
            omniverse_score * 0.1 +
            (1 - crowd_risk) * 0.1 -
            overfit_penalty
        )
        
        # Store metrics for elite selection
        individual.metrics = {
            'in_sample': is_metrics,
            'out_of_sample': oos_metrics,
            'causal_score': causal_score,
            'omniverse_score': omniverse_score,
            'crowd_risk': crowd_risk,
            'overfit_penalty': overfit_penalty
        }
        
        return fitness,
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 0.0,

def init_toolbox():
    """Initialize evolutionary operators with enhanced adaptive mutation"""
    toolbox.register("evaluate", evaluate)
    toolbox.register("select", tools.selTournament, tournsize=7)
    
    # Enhanced fitness-based crossover
    def fitness_cx(ind1, ind2):
        """Fitness-proportional blending crossover"""
        f1 = max(ind1.fitness.values[0], 0.01)  # Avoid division by zero
        f2 = max(ind2.fitness.values[0], 0.01)
        alpha = f1 / (f1 + f2)
        
        for i in range(len(ind1)):
            avg = alpha * ind1[i] + (1 - alpha) * ind2[i]
            ind1[i] = int(avg + random.gauss(0, 0.1))
            ind2[i] = int(avg + random.gauss(0, 0.1))
        return ind1, ind2
    
    toolbox.register("mate", fitness_cx)
    
    # Enhanced fitness-aware mutation
    def adaptive_mutate(individual):
        # Base parameters
        base_mutation_prob = 0.5
        base_sigma = 0.1
        
        if hasattr(individual, 'fitness') and individual.fitness.valid:
            fitness = individual.fitness.values[0]
            
            # Fitness-rank-based probability scaling
            rank_factor = 1 / (1 + math.exp(-fitness))  # Sigmoid mapping
            mutation_prob = base_mutation_prob * (1.5 - rank_factor)  # Higher mutation for lower fitness
            
            # Fitness-distance correlation for step size
            sigma = base_sigma * (1.0 - rank_factor) + 0.01  # Smaller steps for higher fitness
            
            # Apply mutation with fitness-aware parameters
            return tools.mutGaussian(individual, mu=0, sigma=sigma, indpb=mutation_prob)
        else:
            # Default mutation for unevaluated individuals
            return tools.mutGaussian(individual, mu=0, sigma=base_sigma, indpb=base_mutation_prob)
    
    toolbox.register("mutate", adaptive_mutate)

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
            live_stats = st.empty()
            # Add placeholder for 3D visualization
            viz_placeholder = st.empty()
        
        init_toolbox()
        pop = toolbox.population(n=1200)
        
        # Evolutionary loop
        hof = tools.HallOfFame(5)  # Keep top 5 performers
        stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        stats.register("avg", np.mean)
        stats.register("max", np.max)
        stats.register("min", np.min)
        stats.register("std", np.std)
        
        # Data collection for visualization
        generation_data = []
        
        elite_counter = 0
        for gen in range(50):
            if ui_context:
                status_text.text(f"🔥 Generation {gen+1}/50 | Population: 1200 | Elites: {elite_counter}")
                progress_bar.progress((gen+1)/50)
            
            # Evaluate population
            pop = parallel_evaluate(pop)
            hof.update(pop)
            
            # Record and display stats
            record = stats.compile(pop)
            
            # Collect data for visualization
            gen_data = {
                "generation": gen+1,
                "avg_fitness": record['avg'],
                "max_fitness": record['max'],
                "min_fitness": record['min'],
                "diversity": record['std'],
                "top_individuals": [ind[:] for ind in tools.selBest(pop, 5)]
            }
            generation_data.append(gen_data)
            
            if ui_context:
                live_stats.markdown(f"""
                **Population Stats**  
                Avg Fitness: `{record['avg']:.2f}`  
                Max Fitness: `{record['max']:.2f}`  
                Min Fitness: `{record['min']:.2f}`  
                Diversity: `{record['std']:.4f}`
                """)
                
                # Create 3D visualization
                if gen > 0:  # Wait until we have at least 2 generations
                    with viz_placeholder.container():
                        st.subheader("HOLOGRAPHIC EVOLUTIONARY TRAJECTORY")
                        fig = go.Figure()
                        
                        # Add fitness trajectory
                        gens = [gd['generation'] for gd in generation_data]
                        avg_fit = [gd['avg_fitness'] for gd in generation_data]
                        max_fit = [gd['max_fitness'] for gd in generation_data]
                        
                        fig.add_trace(go.Scatter3d(
                            x=gens, y=avg_fit, z=max_fit,
                            mode='lines+markers',
                            marker=dict(size=4, color='#00f3ff'),
                            line=dict(width=6, color='#00b8ff'),
                            name='Fitness Trajectory'
                        ))
                        
                        # Add top individuals as points
                        for i, gd in enumerate(generation_data):
                            for j, ind in enumerate(gd['top_individuals']):
                                fig.add_trace(go.Scatter3d(
                                    x=[i+1], y=[gd['avg_fitness']], z=[gd['max_fitness']],
                                    mode='markers',
                                    marker=dict(
                                        size=8,
                                        color=[f'rgba({j*50}, {255-j*25}, 255, {0.7})'],
                                        symbol='diamond'
                                    ),
                                    name=f'Top Strategy G{i+1}-{j+1}'
                                ))
                        
                        fig.update_layout(
                            scene=dict(
                                xaxis_title='Generation',
                                yaxis_title='Avg Fitness',
                                zaxis_title='Max Fitness',
                                bgcolor='rgba(0,0,0,0)'
                            ),
                            margin=dict(l=0, r=0, b=0, t=0),
                            height=500,
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            # Select next generation (elitism + offspring)
            elites = tools.selBest(pop, int(len(pop)*0.05))  # Top 5%
            offspring = toolbox.select(pop, len(pop) - len(elites))
            offspring = [toolbox.clone(ind) for ind in offspring]
            
            # Crossover with increased rate
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.85:  # Higher crossover rate
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            
            # Adaptive mutation
            for mutant in offspring:
                if random.random() < 0.5:  # Higher mutation rate
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
            
            # Evaluate new individuals
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            invalid_ind = parallel_evaluate(invalid_ind)
            
            # Replace population (elites + offspring)
            pop[:] = elites + offspring
            
            # Auto-deploy elite performers with strict criteria
            for best in hof:
                metrics = getattr(best, 'metrics', {})
                oos_metrics = metrics.get('out_of_sample', {})
                
                if (best.fitness.values[0] > 3.5 and 
                    oos_metrics.get('sharpe', 0) > 3.5 and 
                    oos_metrics.get('max_drawdown', 0) > -0.1 and 
                    metrics.get('omniverse_score', 0) > 0.7 and
                    metrics.get('overfit_penalty', 1) < 0.3):  # Low overfitting
                    
                    name = f"EvoAlpha_{random.randint(10000,99999)}"
                    desc = f"{current_hypothesis} – evolved through Moonshot v4"
                    
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
