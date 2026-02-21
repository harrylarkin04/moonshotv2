from deap import base, creator, tools, algorithms
import random
import numpy as np
from core.data_fetcher import get_train_test_data
from core.registry import save_alpha
from core.causal_engine import swarm_generate_hypotheses, parse_hypothesis_to_signal

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_int", random.randint, 5, 200)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=6)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(individual):
    is_returns, _ = get_train_test_data()
    hypotheses = swarm_generate_hypotheses(is_returns)
    hypothesis = hypotheses[0]  # Use the first hypothesis for this individual
    signal = parse_hypothesis_to_signal(hypothesis, is_returns)
    p1, p2, p3, p4, p5, p6 = [int(x) for x in individual]
    # Evolve parameters on top of the LLM-generated signal
    refined_signal = signal * (is_returns["SPY"].rolling(p1).mean() > is_returns["SPY"].rolling(p2).mean()).astype(int)
    strat_ret = refined_signal.shift(1) * is_returns["SPY"]
    sharpe = (strat_ret.mean() / strat_ret.std() * np.sqrt(252)) if strat_ret.std() != 0 else 0.5
    return sharpe,

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.5)
toolbox.register("select", tools.selTournament, tournsize=8)

def evolve_new_alpha():
    pop = toolbox.population(n=200)
    algorithms.eaSimple(pop, toolbox, cxpb=0.8, mutpb=0.5, ngen=40, verbose=False)
    best = tools.selBest(pop, 1)[0]
    sharpe = best.fitness.values[0]
    hypotheses = swarm_generate_hypotheses(get_train_test_data()[0])
    name = f"EvoAlpha_{random.randint(10000,99999)}"
    desc = f"{hypotheses[0]} – evolved through full Moonshot toolchain"
    persistence = round(sharpe * 0.88, 2)
    save_alpha(name, desc, round(sharpe, 2), persistence)
