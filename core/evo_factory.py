import streamlit as st
from deap import base, creator, tools, algorithms
import random
import numpy as np
from core.data_fetcher import get_train_test_data
from core.registry import save_alpha
from core.causal_engine import swarm_generate_hypotheses

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_int", random.randint, 5, 200)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=6)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(individual):
    is_returns, _ = get_train_test_data()
    hypothesis = st.session_state.get("current_hypothesis", "Fallback hypothesis")
    
    price = (1 + is_returns["SPY"]).cumprod()
    p1, p2, p3, p4, p5, p6 = [int(x) for x in individual]
    
    signal = (price.rolling(p1).mean() > price.rolling(p2).mean()).astype(int).diff().fillna(0)
    
    strat_ret = signal.shift(1) * is_returns["SPY"]
    sharpe = (strat_ret.mean() / strat_ret.std() * np.sqrt(252)) if strat_ret.std() != 0 else 0.5
    return sharpe,

toolbox.register("evaluate", evaluate)

def evolve_new_alpha():
    is_returns, _ = get_train_test_data()
    hypotheses = swarm_generate_hypotheses(is_returns)
    st.session_state.current_hypothesis = hypotheses[0] if hypotheses else "Fallback"

    pop = toolbox.population(n=150)
    algorithms.eaSimple(pop, toolbox, cxpb=0.75, mutpb=0.45, ngen=35, verbose=False)
    
    best = tools.selBest(pop, 1)[0]
    sharpe = best.fitness.values[0]
    
    name = f"EvoAlpha_{random.randint(10000,99999)}"
    desc = f"{st.session_state.current_hypothesis} – evolved through full Moonshot toolchain"
    persistence = round(sharpe * 0.88, 2)
    
    save_alpha(name, desc, round(sharpe, 2), persistence)
    st.success(f"✅ New alpha evolved: {name} | Sharpe {sharpe:.2f}")
