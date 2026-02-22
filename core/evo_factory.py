import streamlit as st
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

# Configure parallel processing
MAX_WORKERS = 8
logger = logging.getLogger(__name__)

# Quantum novelty preservation system
NOVELTY_ARCHIVE = []
BEHAVIOR_CHARACTERIZATION = {}
NOVELTY_DYNAMIC_THRESHOLD = 0.5  # Dynamic threshold for novelty preservation
COV_MATRIX = None  # For Mahalanobis distance

# Remove existing creator classes to avoid conflicts
if "FitnessMax" in creator.__dict__:
    del creator.FitnessMax
if "Individual" in creator.__dict__:
    del creator.Individual

# Enhanced fitness with novelty objective
creator.create("FitnessMax", base.Fitness, weights=(1.0, 0.5, -0.2, 0.3, 0.4, 0.2))  # Added counterfactual weight
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_int", random.randint, 5, 200)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=10)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def characterize_behavior(individual, returns):
    """Create behavioral fingerprint for novelty detection"""
    params = [int(x) for x in individual]
    asset_weights = np.array(params[:4])[:len(returns.columns)]
    asset_weights = asset_weights / asset_weights.sum()
    
    # Generate strategy signals
    signals = pd.DataFrame()
    for col in returns.columns:
        price = (1 + returns[col]).cumprod()
        sma_signal = (price.rolling(params[4]).mean() > price.rolling(params[5]).mean()).astype(int)
        rsi = 100 - (100 / (1 + (returns[col].rolling(params[6]).mean() / abs(returns[col]).rolling(params[6]).mean())))
        rsi_signal = (rsi > params[7]).astype(int)
        signals[col] = (sma_signal * 0.6 + rsi_signal * 0.4)
    
    # Enhanced behavioral fingerprint
    position = signals.rolling(params[5]).mean().diff().fillna(0)
    turnover = position.diff().abs().mean().mean()
    vol = returns.std().mean()
    corr = returns.corrwith(position.shift(1)).mean()
    
    fingerprint = [
        position.mean().mean(),
        position.std().mean(),
        position.skew().mean(),
        position.kurtosis().mean(),
        (position > 0).mean().mean(),
        position.autocorr().mean(),
        turnover,
        vol,
        corr
    ]
    return tuple(fingerprint)

def calculate_novelty(individual, population, archive):
    """Quantum-inspired novelty metric with entanglement"""
    global COV_MATRIX
    all_points = list(BEHAVIOR_CHARACTERIZATION.values()) + archive
    if len(all_points) < 2:
        return 0.0
    
    # Calculate Mahalanobis distance for novelty
    behaviors = np.array(all_points)
    if COV_MATRIX is None or COV_MATRIX.shape[0] != behaviors.shape[1]:
        try:
            cov = np.cov(behaviors, rowvar=False)
            COV_MATRIX = inv(cov + np.eye(cov.shape[0]) * 1e-6)
        except:
            COV_MATRIX = np.eye(behaviors.shape[1])
    
    ind_index = list(BEHAVIOR_CHARACTERIZATION.keys()).index(id(individual))
    target = behaviors[ind_index]
    distances = []
    for i, point in enumerate(behaviors):
        if i != ind_index:
            try:
                dist = mahalanobis(target, point, COV_MATRIX)
                distances.append(dist)
            except:
                distances.append(euclidean(target, point))
    
    k = min(15, len(distances))
    distances.sort()
    return np.mean(distances[:k])

def calculate_diversity(population):
    """Enhanced diversity calculation with quantum entanglement"""
    if len(population) < 2:
        return 0.0, np.array([]), np.array([])
    
    # Behavioral diversity
    behaviors = [BEHAVIOR_CHARACTERIZATION.get(id(ind), np.zeros(9)) for ind in population]
    centroid = np.mean(behaviors, axis=0)
    distances = [euclidean(b, centroid) for b in behaviors]
    diversity_index = np.mean(distances)
    
    # 3D PCA projection for diversity visualization
    if len(behaviors) >= 3:
        pca = PCA(n_components=3)
        projection = pca.fit_transform(behaviors)
    else:
        projection = np.zeros((len(population), 3))
    
    return diversity_index, projection, np.array(behaviors)

def backtest(individual, returns, fold_count=5):
    """Enhanced backtesting with liquidity-aware position sizing"""
    if len(returns.columns) < 3:
        raise ValueError("Insufficient assets for portfolio construction")
    
    # Extract parameters
    params = [int(x) for x in individual]
    if len(params) < 10:
        params = params + [random.randint(5,200) for _ in range(10-len(params))]
    p1, p2, p3, p4, p5, p6, p7, p8, p9, p10 = params
    
    # Portfolio construction with liquidity constraints
    asset_weights = np.array(params[:4])[:len(returns.columns)]
    asset_weights = asset_weights / asset_weights.sum()
    
    # Walk-forward validation with multiple folds
    fold_size = len(returns) // fold_count
    wf_results = []
    all_returns = pd.Series(dtype=float)
    
    for fold in range(fold_count):
        start_idx = fold * fold_size
        end_idx = (fold + 1) * fold_size if fold < fold_count - 1 else len(returns)
        chunk = returns.iloc[start_idx:end_idx]
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
        
        # Adaptive position sizing with liquidity constraints
        position = signals.rolling(p6).mean().diff().fillna(0)
        position = position.clip(lower=-1, upper=1) * p7 / 100.0
        
        # Apply liquidity-aware execution trajectory
        for asset in position.columns:
            position[asset] = optimal_execution_trajectory(
                adv=position[asset].mean(),
                position=position[asset],
                horizon=30
            )
        
        # Realistic impact simulation
        position_changes = position.diff().fillna(0)
        impact_costs = position_changes.abs() * 0.0005  # Institutional costs
        weighted_returns = (position.shift(1) * returns - impact_costs).sum(axis=1)
        all_returns = pd.concat([all_returns, weighted_returns])
        
        # Performance metrics with Sortino ratio
        cumulative = (1 + weighted_returns).cumprod()
        peak = cumulative.expanding(min_periods=1).max()
        drawdown = (cumulative - peak) / peak
        
        returns_std = weighted_returns.std()
        downside_returns = weighted_returns[weighted_returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
        
        sharpe = (weighted_returns.mean() / returns_std * np.sqrt(252)) if returns_std != 0 else 0
        sortino = (weighted_returns.mean() / downside_std * np.sqrt(252)) if downside_std != 0 else 0
        max_drawdown = drawdown.min()
        capacity = 1e9 * (1 / position.abs().max().max()) if position.abs().max().max() > 0 else 1e9
        
        wf_results.append({
            'sharpe': sharpe,
            'sortino': sortino,
            'max_drawdown': max_drawdown,
            'capacity': capacity,
            'fold': fold
        })
    
    # Aggregate results with consistency metric
    if not wf_results:
        return {'sharpe': 0, 'sortino': 0, 'max_drawdown': 0, 'capacity': 0, 'consistency': 0}, all_returns
    
    sharpe_std = np.std([r['sharpe'] for r in wf_results])
    avg_sharpe = np.mean([r['sharpe'] for r in wf_results])
    avg_sortino = np.mean([r['sortino'] for r in wf_results])
    consistency = max(0, 1 - sharpe_std / avg_sharpe) if avg_sharpe != 0 else 0
    
    return {
        'sharpe': avg_sharpe,
        'sortino': avg_sortino,
        'max_drawdown': np.mean([r['max_drawdown'] for r in wf_results]),
        'capacity': np.mean([r['capacity'] for r in wf_results]),
        'consistency': consistency
    }, all_returns

def test_counterfactual_resilience(individual, returns):
    """Test strategy resilience under multiple market shock scenarios"""
    resilience_scores = []
    shock_scenarios = [
        ("negative", -0.1),
        ("negative", -0.15),
        ("positive", 0.1),
        ("volatility", 0.2)
    ]
    
    for scenario in shock_scenarios:
        shock_type, shock_size = scenario
        for asset in returns.columns[:3]:  # Test top 3 assets
            try:
                # Apply shock based on scenario type
                if shock_type == "volatility":
                    # Increase volatility by shock_size
                    shocked_returns = returns.copy()
                    shocked_returns[asset] = shocked_returns[asset] * (1 + shock_size)
                else:
                    # Price shock
                    shocked_returns = counterfactual_sim(
                        returns, 
                        shock_asset=asset, 
                        shock_size=shock_size,
                        steps=120
                    )
                
                # Backtest on shocked returns
                metrics, _ = backtest(individual, shocked_returns, fold_count=1)
                base_metrics, _ = backtest(individual, returns, fold_count=1)
                
                # Calculate resilience score
                sharpe_drop = base_metrics['sharpe'] - metrics['sharpe']
                resilience = max(0, 1 - abs(sharpe_drop) / max(0.1, base_metrics['sharpe']))
                resilience_scores.append(resilience)
            except:
                resilience_scores.append(0.0)
    
    # Weighted average with more weight to severe scenarios
    weights = [1.0, 1.2, 0.8, 1.1]
    weighted_scores = [s * w for s, w in zip(resilience_scores, weights)]
    return np.sum(weighted_scores) / np.sum(weights)

def evaluate(individual):
    """Enhanced evaluation with quantum novelty scoring"""
    try:
        is_returns, oos_returns = get_train_test_data()
        is_metrics, strategy_returns = backtest(individual, is_returns, fold_count=5)
        
        # Behavioral characterization for novelty
        BEHAVIOR_CHARACTERIZATION[id(individual)] = characterize_behavior(individual, is_returns)
        
        # Neural validation gate
        X = np.array(individual).reshape(1, -1)
        y = np.array([is_metrics['sharpe']])
        nn = MLPRegressor(hidden_layer_sizes=(20,), max_iter=100)
        nn.fit(X, y)
        nn_sharpe = nn.predict(X)[0]
        
        if abs(is_metrics['sharpe'] - nn_sharpe) > 0.5:
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        
        # Full pipeline validation
        if not swarm_generate_hypotheses(is_returns):
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        
        G = build_causal_dag(is_returns)
        causal_score = len(G.edges) / 100
        
        omniverse_score = run_omniverse_sims(scenario="Stress", num_sims=5000)
        crowd_risk = simulate_cascade_prob()
        
        oos_metrics, _ = backtest(individual, oos_returns, fold_count=3)
        overfit_penalty = abs(is_metrics['sharpe'] - oos_metrics['sharpe']) * 0.7
        
        # Counterfactual resilience testing
        resilience_score = test_counterfactual_resilience(individual, oos_returns)
        
        # Composite fitness score with quantum entanglement
        fitness = (
            oos_metrics['sharpe'] * 0.4 + 
            oos_metrics['sortino'] * 0.15 +
            (1 - abs(oos_metrics['max_drawdown'])) * 0.15 +
            omniverse_score * 0.1 +
            (1 - crowd_risk) * 0.05 -
            overfit_penalty +
            oos_metrics['consistency'] * 0.1 +
            resilience_score * 0.2
        )
        
        individual.metrics = {
            'in_sample': is_metrics,
            'out_of_sample': oos_metrics,
            'causal_score': causal_score,
            'omniverse_score': omniverse_score,
            'crowd_risk': crowd_risk,
            'overfit_penalty': overfit_penalty,
            'neural_validation': nn_sharpe,
            'consistency': oos_metrics['consistency'],
            'resilience_score': resilience_score
        }
        
        return fitness, oos_metrics['consistency'], causal_score, oos_metrics['sortino'], 0.0, resilience_score
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

def init_toolbox():
    """Initialize with quantum novelty preservation"""
    toolbox.register("evaluate", evaluate)
    toolbox.register("select", tools.selTournament, tournsize=7)
    
    def quantum_entanglement_mate(ind1, ind2, temperature=0.5):
        """Quantum-inspired crossover with entanglement"""
        f1 = max(ind1.fitness.values[0], 0.01)
        f2 = max(ind2.fitness.values[0], 0.01)
        alpha = f1 / (f1 + f2) * (1 + np.random.normal(0, temperature))
        
        # Enhanced entanglement effect - correlated parameters
        entanglement_mask = [random.random() < 0.3 for _ in range(len(ind1))]
        entanglement_group = random.sample(range(len(ind1)), k=min(4, len(ind1)//2))
        
        for i in range(len(ind1)):
            if i in entanglement_group or entanglement_mask[i]:
                avg = alpha * ind1[i] + (1 - alpha) * ind2[i]
                ind1[i] = int(avg + random.gauss(0, 0.1))
                ind2[i] = int(avg + random.gauss(0, 0.1))
            else:
                # Swap parameters with probability
                if random.random() < 0.4:
                    ind1[i], ind2[i] = ind2[i], ind1[i]
        return ind1, ind2
    
    toolbox.register("mate", quantum_entanglement_mate, temperature=0.3)
    
    def adaptive_mutate(individual, diversity, generation):
        """Adaptive mutation based on diversity and generation"""
        base_mutation_prob = 0.3
        diversity_factor = 1.0 - min(diversity, 0.8) / 0.8
        mutation_prob = base_mutation_prob * diversity_factor
        generation_factor = max(0.5, 1.0 - generation / 100.0)
        mutation_prob *= generation_factor
        
        # Use diversity to adjust mutation strength
        sigma = 0.1 * (1.0 - min(diversity, 0.8)) + 0.01
        return tools.mutGaussian(individual, mu=0, sigma=sigma, indpb=mutation_prob)
    
    toolbox.register("mutate", adaptive_mutate)

def parallel_evaluate(population):
    """Parallel evaluation with novelty scoring"""
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(toolbox.evaluate, ind) for ind in population]
        results = [f.result() for f in futures]
    
    # Calculate novelty scores
    for ind in population:
        novelty = calculate_novelty(ind, population, NOVELTY_ARCHIVE)
        ind.fitness.novelty = novelty
    
    # Update archive with novel individuals
    avg_novelty = np.mean([ind.fitness.novelty for ind in population])
    global NOVELTY_DYNAMIC_THRESHOLD
    NOVELTY_DYNAMIC_THRESHOLD = max(0.3, min(0.7, avg_novelty * 1.2))  # Dynamic threshold adjustment
    
    for ind in population:
        if ind.fitness.novelty > NOVELTY_DYNAMIC_THRESHOLD:
            NOVELTY_ARCHIVE.append(BEHAVIOR_CHARACTERIZATION[id(ind)])
    
    # Combine results with novelty
    for ind, (fit, consistency, causal, sortino, _, resilience) in zip(population, results):
        ind.fitness.values = (fit, consistency, causal, sortino, ind.fitness.novelty, resilience)
    return population

def evolve_new_alpha(ui_context=False):
    """Enhanced evolution with quantum novelty preservation"""
    try:
        global NOVELTY_ARCHIVE, BEHAVIOR_CHARACTERIZATION, COV_MATRIX
        NOVELTY_ARCHIVE = []
        BEHAVIOR_CHARACTERIZATION = {}
        COV_MATRIX = None
        
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
            novelty_placeholder = st.empty()
            resilience_placeholder = st.empty()
            entanglement_placeholder = st.empty()  # New entanglement visualization
            
            with st.sidebar.expander("⚡ QUANTUM EVOLUTION CONTROLS"):
                st.session_state.quantum_temp = st.slider("Quantum Temperature", 0.1, 1.0, 0.3, 0.05)
                st.session_state.diversity_threshold = st.slider("Diversity Threshold", 0.1, 0.9, 0.4, 0.05)
                st.session_state.novelty_weight = st.slider("Novelty Weight", 0.1, 1.0, 0.4, 0.05)
                st.session_state.resilience_weight = st.slider("Resilience Weight", 0.1, 1.0, 0.2, 0.05)
                st.session_state.neural_validation = st.checkbox("Neural Validation Gate", True)
                st.session_state.fold_count = st.slider("Validation Folds", 3, 10, 5, 1)
                st.session_state.pop_size = st.slider("Population Size", 500, 2000, 1200, 100)
                st.session_state.entanglement_strength = st.slider("Entanglement Strength", 0.1, 0.9, 0.3, 0.05)
                st.session_state.shock_size = st.slider("Resilience Shock Size", -0.3, -0.01, -0.1, 0.01)
                st.session_state.shock_scenarios_count = st.slider("Shock Scenarios", 1, 5, 4, 1)
        
        init_toolbox()
        pop = toolbox.population(n=st.session_state.pop_size if ui_context else 1200)
        
        hof = tools.HallOfFame(5)
        stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        stats.register("avg", np.mean)
        stats.register("max", np.max)
        stats.register("min", np.min)
        stats.register("std", np.std)
        
        generation_data = []
        diversity_history = []
        novelty_history = []
        resilience_history = []
        best_fitness_history = []
        entanglement_history = []  # Track entanglement strength
        stagnation_counter = 0
        prev_best = -np.inf
        
        elite_counter = 0
        for gen in range(50):
            if ui_context:
                status_text.text(f"🌌 Generation {gen+1}/50 | Quantum Temp: {st.session_state.quantum_temp:.2f}")
                progress_bar.progress((gen+1)/50)
            
            pop = parallel_evaluate(pop)
            hof.update(pop)
            
            diversity, projection, behaviors = calculate_diversity(pop)
            diversity_history.append(diversity)
            novelty_history.append(np.mean([ind.fitness.values[4] for ind in pop]))
            resilience_history.append(np.mean([ind.fitness.values[5] for ind in pop]))
            
            record = stats.compile(pop)
            current_best = record['max']
            
            # Quantum annealing temperature adjustment
            if current_best <= prev_best + 0.001:
                stagnation_counter += 1
                if stagnation_counter > 3:
                    st.session_state.quantum_temp = min(1.0, st.session_state.quantum_temp + 0.15)
                    stagnation_counter = 0
            else:
                stagnation_counter = 0
                st.session_state.quantum_temp = max(0.1, st.session_state.quantum_temp - 0.05)
            prev_best = current_best
            
            gen_data = {
                "generation": gen+1,
                "avg_fitness": record['avg'],
                "max_fitness": record['max'],
                "min_fitness": record['min'],
                "diversity": diversity,
                "novelty": np.mean([ind.fitness.novelty for ind in pop]),
                "resilience": np.mean([ind.fitness.values[5] for ind in pop]),
                "projection": projection,
                "behaviors": behaviors,
                "top_individuals": [ind[:] for ind in tools.selBest(pop, 5)]
            }
            generation_data.append(gen_data)
            
            if ui_context:
                live_stats.markdown(f"""
                **QUANTUM FIELD**  
                Max Fitness: `{record['max']:.2f}` ⚡  
                Diversity: `{diversity:.4f}` 🌐  
                Novelty: `{gen_data['novelty']:.4f}` 🌀  
                Resilience: `{gen_data['resilience']:.4f}` 🛡️  
                Stagnation: `{stagnation_counter}/3` ⏳  
                Elites: `{elite_counter}` 🚀
                """)
                
                # Enhanced holographic visualization
                with diversity_placeholder.container():
                    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'scatter3d'}, {'type': 'scatter'}]])
                    
                    # 3D quantum field projection
                    if projection.shape[1] == 3:
                        fig.add_trace(go.Scatter3d(
                            x=projection[:,0], y=projection[:,1], z=projection[:,2],
                            mode='markers',
                            marker=dict(
                                size=6,
                                color=[ind.fitness.values[5] for ind in pop],  # Resilience-based coloring
                                colorscale='Portland',
                                opacity=0.9,
                                line=dict(width=1, color='#00f3ff')
                            ),
                            name='Quantum Field'
                        ), row=1, col=1)
                    
                    # Fitness trajectory
                    gens = [gd['generation'] for gd in generation_data]
                    max_fit = [gd['max_fitness'] for gd in generation_data]
                    fig.add_trace(go.Scatter(
                        x=gens, y=max_fit,
                        mode='lines+markers',
                        line=dict(color='#00f3ff', width=4),
                        marker=dict(size=8, symbol='diamond'),
                        name='Fitness Trajectory'
                    ), row=1, col=2)
                    
                    fig.update_layout(
                        title="HOLOGRAPHIC QUANTUM FIELD",
                        template='plotly_dark',
                        height=500,
                        margin=dict(l=20, r=20, t=80, b=20),
                        scene=dict(
                            xaxis_title='Entanglement Axis 1',
                            yaxis_title='Entanglement Axis 2',
                            zaxis_title='Resilience Axis'
                        )
                    )
                    hologram_placeholder.plotly_chart(fig, use_container_width=True)
                    
                # Novelty visualization
                with novelty_placeholder.container():
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=gens, y=novelty_history,
                        mode='lines+markers',
                        line=dict(color='#ff00ff', width=3),
                        name='Novelty Score'
                    ))
                    fig.update_layout(
                        title="NOVELTY EVOLUTION",
                        template='plotly_dark',
                        height=300,
                        xaxis_title='Generation',
                        yaxis_title='Novelty',
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                # Resilience visualization
                with resilience_placeholder.container():
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=gens, y=resilience_history,
                        mode='lines+markers',
                        line=dict(color='#00ff00', width=3),
                        name='Resilience Score'
                    ))
                    fig.update_layout(
                        title="RESILIENCE EVOLUTION",
                        template='plotly_dark',
                        height=300,
                        xaxis_title='Generation',
                        yaxis_title='Resilience',
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                # Entanglement visualization
                with entanglement_placeholder.container():
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=gens, 
                        y=[st.session_state.quantum_temp for _ in gens],
                        mode='lines+markers',
                        line=dict(color='#ff5500', width=3),
                        name='Quantum Temperature'
                    ))
                    fig.update_layout(
                        title="QUANTUM ENTANGLEMENT EVOLUTION",
                        template='plotly_dark',
                        height=300,
                        xaxis_title='Generation',
                        yaxis_title='Temperature',
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Select next generation with diversity preservation
            elites = tools.selBest(pop, int(len(pop)*0.05))
            offspring = toolbox.select(pop, len(pop) - len(elites))
            offspring = [toolbox.clone(ind) for ind in offspring]
            
            # Apply quantum crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.85:
                    toolbox.mate(child1, child2, temperature=st.session_state.quantum_temp)
                    del child1.fitness.values
                    del child2.fitness.values
            
            # Apply adaptive mutation
            for mutant in offspring:
                if random.random() < 0.5:
                    toolbox.mutate(mutant, diversity, gen)
                    del mutant.fitness.values
            
            # Re-evaluate mutated individuals
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            invalid_ind = parallel_evaluate(invalid_ind)
            pop[:] = elites + offspring
            
            # Elite deployment with holographic validation
            for best in hof:
                metrics = getattr(best, 'metrics', {})
                oos_metrics = metrics.get('out_of_sample', {})
                
                if (best.fitness.values[0] > 3.5 and 
                    oos_metrics.get('sharpe', 0) > 3.5 and 
                    oos_metrics.get('sortino', 0) > 3.0 and
                    oos_metrics.get('max_drawdown', 0) > -0.1 and 
                    metrics.get('omniverse_score', 0) > 0.7 and
                    metrics.get('overfit_penalty', 1) < 0.2 and
                    diversity > st.session_state.diversity_threshold and
                    metrics.get('consistency', 0) > 0.7 and
                    best.fitness.values[4] > NOVELTY_DYNAMIC_THRESHOLD and
                    best.fitness.values[5] > 0.7):  # Added resilience threshold
                    
                    name = f"QuantumAlpha_{random.randint(10000,99999)}"
                    desc = f"{current_hypothesis} – evolved through Quantum Evo v8"
                    
                    if save_alpha(
                        name, 
                        desc, 
                        round(oos_metrics['sharpe'], 2), 
                        round(1 - abs(metrics['in_sample']['sharpe'] - oos_metrics['sharpe']), 2),
                        metrics=json.dumps(metrics),
                        diversity=diversity,
                        novelty=best.fitness.values[4],
                        resilience=best.fitness.values[5]
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
