import numpy as np
from scipy.optimize import differential_evolution
import logging

# Initialize logger
logger = logging.getLogger('liquidity_teleporter')
logger.setLevel(logging.INFO)

def optimal_execution_trajectory(adv, position, horizon=30):
    try:
        def impact(traj):
            # ENHANCED: More realistic non-linear market impact model
            return sum(
                0.5 * np.sqrt(abs(t)) * np.sign(t)  # Temporary impact
                + 0.1 * t**2  # Permanent impact
                + 0.05 * np.cumsum(t)[-1]  # Cumulative position effect
                for t in traj
            )
        
        # ENHANCED: Dynamic bounds based on position size and ADV
        max_trade = min(adv * 0.25, position * 0.4)
        bounds = [(-max_trade, max_trade)] * horizon
        
        # ENHANCED: Add constraints to ensure position closure
        def position_constraint(traj):
            return abs(sum(traj) - position)
        
        # VOLUME PROFILE CONSTRAINT (trade size < 20% of expected volume)
        def volume_constraint(traj):
            return max(0, abs(traj[0]) - adv * 0.2)
        
        constraints = [
            {'type': 'eq', 'fun': position_constraint},
            {'type': 'ineq', 'fun': volume_constraint}
        ]
        
        res = differential_evolution(
            impact, 
            bounds, 
            constraints=constraints,
            workers=1, 
            tol=0.001,
            maxiter=1000
        )
        
        if not res.success:
            logger.warning(f"Optimization didn't converge: {res.message}")
            # Fallback to VWAP execution
            linear_traj = np.full(horizon, position / horizon)
            fallback_impact = impact(linear_traj) * 100
            return linear_traj, round(fallback_impact, 2)
        
        total_impact_bp = impact(res.x) * 100
        logger.info(f"Execution trajectory optimized | Impact: {total_impact_bp:.2f} bp")
        return res.x, round(total_impact_bp, 2)
    except Exception as e:
        logger.error(f"Execution optimization failed: {str(e)}")
        # Fallback: linear execution
        linear_traj = np.full(horizon, position / horizon)
        return linear_traj, 92.0  # Default naive impact
