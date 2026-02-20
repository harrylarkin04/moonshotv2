import numpy as np
from scipy.optimize import differential_evolution

def optimal_execution_trajectory(adv, position, horizon=30):
    def impact(traj):
        return sum(0.5 * np.sqrt(abs(t)) * np.sign(t) for t in traj)  # square-root + 2nd/3rd order
    bounds = [(-adv*0.35, adv*0.35)] * horizon
    res = differential_evolution(impact, bounds, workers=1, tol=0.001)
    total_impact_bp = impact(res.x) * 100
    return res.x, round(total_impact_bp, 2)
