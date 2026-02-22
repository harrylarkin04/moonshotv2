import streamlit as st
from deap import base, creator, tools, algorithms
import random
import numpy as np
import pandas as pd
import logging
import json
import math
from scipy.spatial.distance import euclidean
from concurrent.futures import ProcessPoolExecutor
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.neural_network import MLPRegressor
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
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=10)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def calculate_diversity(population):
    """Calculate population diversity using Euclidean distance with 3D mapping"""
    if len(population) < 2:
        return 0.0, np.array([])
    
    pop_array = np.array(population)
    centroid = np.mean(pop_array, axis=0)
    
    # 3D PCA projection for diversity visualization
    if pop_array.shape[1] >= 3:
        cov = np.cov(pop_array.T)
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        order = np.argsort(eigenvalues)[::-1]
        projection = pop_array.dot(eigenvectors[:, order[:3]])
    else:
        projection = np.zeros((len(population), 3))
    
    distances = [euclidean(ind, centroid) for ind in population]
    return np.mean(distances), projection

def backtest(individual, returns):
    """Optimized backtesting with vectorized impact simulation"""
    if len(returns.columns) < 3:
        raise ValueError("Insufficient assets for portfolio construction")
    
    # Extract parameters
    params = [int(x) for x in individual]
    p1, p2, p3, p4, p5, p6, p7, p8, p9, p10 = params
    
    # Portfolio construction
    asset_weights = np.array(params[:4])[:len(returns.columns)]
    asset_weights = asset_weights / asset_weights.sum()
    
    # Walk-forward validation
    wf_results = []
    for i in range(0, len(returns)-p9, p10):
        chunk = returns.iloc[i:i+p9]
        if len(chunk) < 30:
            continue
            
        # Vectorized signal generation
        signals = pd.DataFrame()
        for col in returns.columns:
            price = (1 + returns[col]).cumprod()
            sma_signal = (price.rolling(p5).mean() > price.rolling(p6).mean()).astype(int)
            rsi = 100 - (100 / (1 + (returns[col].rolling(p7).mean() / abs(returns[col]).rolling(p7).mean())))
            rsi_signal = (rsi > p8).astype(int)
            signals[col] = (sma_signal * 0.6 + rsi_signal * 0.4)
        
        # Position sizing
        position = signals.rolling(p6).mean().diff().fillna(0)
        position = position.clip(lower=-1, upper=1) * p7 / 100.0
        
        # Vectorized impact simulation
        position_changes = position.diff().fillna(0)
        impact_costs = position_changes.abs() * 0.0001
        weighted_returns = (position.shift(1) * returns - impact_costs).sum(axis=1)
        
        # Performance metrics
        cumulative = (1 + weighted_returns).cumprod()
        peak = cumulative.expanding(min_periods=1).max()
        drawdown = (cumulative - peak) / peak
        
        sharpe = (weighted_returns.mean() / weighted_returns.std() * np.sqrt(252)) if weighted_returns.std() != 0 else 0
        max_drawdown = drawdown.min()
        capacity = 1e9 * (1 / position.abs().max().max()) if position.abs().max().max() > 0 else 1e9
        
        wf_results.append({
            'sharpe': sharpe,
            'max_drawdown': max_drawdown,
            'capacity': capacity
        })
    
    # Aggregate results
    if not wf_results:
        return {'sharpe': 0, 'max_drawdown': 0, 'capacity': 0}
    
    return {
        'sharpe': np.mean([r['sharpe'] for r in wf_results]),
        'max_drawdown': np.mean([r['max_drawdown'] for r in wf_results]),
        'capacity': np.mean([r['capacity'] for r in wf_results])
    }

def evaluate(individual):
    """Enhanced evaluation with neural validation"""
    try:
        is_returns, oos_returns = get_train_test_data()
        is_metrics = backtest(individual, is_returns)
        
        # Neural validation gate
        X = np.array(individual).reshape(1, -1)
        y = np.array([is_metrics['sharpe']])
        nn = MLPRegressor(hidden_layer_sizes=(20,), max_iter=100)
        nn.fit(X, y)
        nn_sharpe = nn.predict(X)[0]
        
        if abs(is_metrics['sharpe'] - nn_sharpe) > 0.5:
            return 0.0,
        
        # Full pipeline validation
        if not swarm_generate_hypotheses(is_returns):
            return 0.0,
        
        G = build_causal_dag(is_returns)
        causal_score = len(G.edges) / 100
        
        omniverse_score = run_omniverse_sims(scenario="Stress", num_sims=5000)
        crowd_risk = simulate_cascade_prob()
        
        oos_metrics = backtest(individual, oos_returns)
        overfit_penalty = abs(is_metrics['sharpe'] - oos_metrics['sharpe']) * 0.7
        
        # Composite fitness score
        fitness = (
            oos_metrics['sharpe'] * 0.7 + 
            (1 - abs(oos_metrics['max_drawdown'])) * 0.15 +
            omniverse_score * 0.1 +
            (1 - crowd_risk) * 0.05 -
            overfit_penalty
        )
        
        individual.metrics = {
            'in_sample': is_metrics,
            'out_of_sample': oos_metrics,
            'causal_score': causal_score,
            'omniverse_score': omniverse_score,
            'crowd_risk': crowd_risk,
            'overfit_penalty': overfit_penalty,
            'neural_validation': nn_sharpe
        }
        
        return fitness,
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 0.0,

def init_toolbox():
    """Initialize with quantum annealing-inspired mutation"""
    toolbox.register("evaluate", evaluate)
    toolbox.register("select", tools.selTournament, tournsize=7)
    
    def quantum_mate(ind1, ind2, temperature=0.5):
        """Quantum-inspired crossover with simulated annealing"""
        f1 = max(ind1.fitness.values[0], 0.01)
        f2 = max(ind2.fitness.values[0], 0.01)
        alpha = f1 / (f1 + f2) * (1 + np.random.normal(0, temperature))
        
        for i in range(len(ind1)):
            avg = alpha * ind1[i] + (1 - alpha) * ind2[i]
            ind1[i] = int(avg + random.gauss(0, 0.1))
            ind2[i] = int(avg + random.gauss(0, 0.1))
        return ind1, ind2
    
    toolbox.register("mate", quantum_mate, temperature=0.3)
    
    def quantum_mutate(individual, diversity, generation):
        """Quantum annealing mutation with temperature schedule"""
        # Temperature decreases with generations
        temperature = max(0.1, 0.5 * np.exp(-generation/50))
        
        # Mutation probability based on diversity
        mutation_prob = 0.5 * (1.0 - min(diversity, 0.8)) * temperature
        
        if hasattr(individual, 'fitness') and individual.fitness.valid:
            fitness = individual.fitness.values[0]
            rank_factor = 1 / (1 + math.exp(-fitness))
            mutation_prob *= (1.5 - rank_factor)
            sigma = 0.1 * (1.0 - rank_factor) + 0.01
        else:
            sigma = 0.1 * (1.0 + (1.0 - diversity))
        
        # Apply quantum tunneling effect
        if random.random() < 0.2:
            idx = random.randint(0, len(individual)-1)
            individual[idx] = random.randint(5, 200)
        
        return tools.mutGaussian(individual, mu=0, sigma=sigma, indpb=mutation_prob)
    
    toolbox.register("mutate", quantum_mutate)

def parallel_evaluate(population):
    """Parallel evaluation with progress tracking"""
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(toolbox.evaluate, ind) for ind in population]
        fitnesses = [f.result() for f in futures]
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit
    return population

def evolve_new_alpha(ui_context=False):
    """Enhanced evolution with 3D visualization and quantum operators"""
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
            diversity_placeholder = st.empty()
            hologram_placeholder = st.empty()
            
            with st.sidebar.expander("⚡ QUANTUM EVOLUTION CONTROLS"):
                st.session_state.quantum_temp = st.slider("Quantum Temperature", 0.1, 1.0, 0.3, 0.05)
                st.session_state.diversity_threshold = st.slider("Diversity Threshold", 0.1, 0.9, 0.4, 0.05)
                st.session_state.neural_validation = st.checkbox("Neural Validation Gate", True)
        
        init_toolbox()
        pop = toolbox.population(n=1200)
        
        hof = tools.HallOfFame(5)
        stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        stats.register("avg", np.mean)
        stats.register("max", np.max)
        stats.register("min", np.min)
        stats.register("std", np.std)
        
        generation_data = []
        diversity_history = []
        best_fitness_history = []
        stagnation_counter = 0
        prev_best = -np.inf
        
        elite_counter = 0
        for gen in range(50):
            if ui_context:
                status_text.text(f"🌌 Generation {gen+1}/50 | Quantum Temp: {st.session_state.quantum_temp:.2f}")
                progress_bar.progress((gen+1)/50)
            
            pop = parallel_evaluate(pop)
            hof.update(pop)
            
            diversity, projection = calculate_diversity(pop)
            diversity_history.append(diversity)
            
            record = stats.compile(pop)
            current_best = record['max']
            
            # Stagnation detection
            if current_best <= prev_best + 0.001:
                stagnation_counter += 1
                if stagnation_counter > 5:
                    # Increase mutation when stagnating
                    st.session_state.quantum_temp = min(1.0, st.session_state.quantum_temp + 0.1)
                    stagnation_counter = 0
            else:
                stagnation_counter = 0
            prev_best = current_best
            
            gen_data = {
                "generation": gen+1,
                "avg_fitness": record['avg'],
                "max_fitness": record['max'],
                "min_fitness": record['min'],
                "diversity": diversity,
                "projection": projection,
                "top_individuals": [ind[:] for ind in tools.selBest(pop, 5)]
            }
            generation_data.append(gen_data)
            
            if ui_context:
                live_stats.markdown(f"""
                **QUANTUM FIELD**  
                Max Fitness: `{record['max']:.2f}` ⚡  
                Diversity: `{diversity:.4f}` 🌐  
                Stagnation: `{stagnation_counter}/5` ⏳  
                Elites: `{elite_counter}` 🚀
                """)
                
                # Holographic diversity visualization
                with diversity_placeholder.container():
                    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'scatter3d'}, {'type': 'scatter'}]])
                    
                    # 3D population projection
                    if projection.shape[1] == 3:
                        fig.add_trace(go.Scatter3d(
                            x=projection[:,0], y=projection[:,1], z=projection[:,2],
                            mode='markers',
                            marker=dict(
                                size=4,
                                color=pop,
                                colorscale='Viridis',
                                opacity=0.8
                            ),
                            name='Population'
                        ), row=1, col=1)
                    
                    # Fitness trajectory
                    gens = [gd['generation'] for gd in generation_data]
                    max_fit = [gd['max_fitness'] for gd in generation_data]
                    fig.add_trace(go.Scatter(
                        x=gens, y=max_fit,
                        mode='lines+markers',
                        line=dict(color='#00f3ff', width=4),
                        name='Max Fitness'
                    ), row=1, col=2)
                    
                    fig.update_layout(
                        title="HOLOGRAPHIC EVOLUTION FIELD",
                        template='plotly_dark',
                        height=400,
                        margin=dict(l=20, r=20, t=60, b=20)
                    )
                    hologram_placeholder.plotly_chart(fig, use_container_width=True)
            
            # Select next generation
            elites = tools.selBest(pop, int(len(pop)*0.05))
            offspring = toolbox.select(pop, len(pop) - len(elites))
            offspring = [toolbox.clone(ind) for ind in offspring]
            
            # Apply quantum crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.85:
                    toolbox.mate(child1, child2, temperature=st.session_state.quantum_temp)
                    del child1.fitness.values
                    del child2.fitness.values
            
            # Apply quantum mutation
            for mutant in offspring:
                if random.random() < 0.5:
                    toolbox.mutate(mutant, diversity, gen)
                    del mutant.fitness.values
            
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            invalid_ind = parallel_evaluate(invalid_ind)
            pop[:] = elites + offspring
            
            # Elite deployment with holographic validation
            for best in hof:
                metrics = getattr(best, 'metrics', {})
                oos_metrics = metrics.get('out_of_sample', {})
                
                if (best.fitness.values[0] > 3.5 and 
                    oos_metrics.get('sharpe', 0) > 3.5 and 
                    oos_metrics.get('max_drawdown', 0) > -0.1 and 
                    metrics.get('omniverse_score', 0) > 0.7 and
                    metrics.get('overfit_penalty', 1) < 0.2 and
                    diversity > st.session_state.diversity_threshold):
                    
                    name = f"QuantumAlpha_{random.randint(10000,99999)}"
                    desc = f"{current_hypothesis} – evolved through Quantum Evo v5"
                    
                    if save_alpha(
                        name, 
                        desc, 
                        round(oos_metrics['sharpe'], 2), 
                        round(1 - abs(metrics['in_sample']['sharpe'] - oos_metrics['sharpe']), 2),
                        metrics=json.dumps(metrics),
                        diversity=diversity
                    ):
                        elite_counter += 1
                        if ui_context:
                            elite_count.text(f"🚀 ELITES DEPLOYED: {elite_counter}")
                            with metrics_display.expander(f"⚡ {name} METRICS"):
                                st.json(metrics)
        
        if ui_context and elite_counter == 0:
            st.warning("🌌 Quantum field collapsed - no elites met resonance criteria")
        return elite_counter > 0
            
    except Exception as e:
        logger.exception("Quantum evolution failed")
        if ui_context:
            st.error(f"⚠️ Quantum decoherence: {str(e)}")
        return False
