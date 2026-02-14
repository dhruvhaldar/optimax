import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint

def solve_cutting_stock(roll_length, demands):
    """
    Solves Cutting Stock problem using Column Generation.
    demands: list of (width, quantity)
    """
    widths = [d[0] for d in demands]
    quantities = [d[1] for d in demands]
    n_items = len(widths)

    # Initial patterns: One roll for each item type (identity matrix like)
    # Actually, a better initial basis is fitting as many of item i as possible
    patterns = []
    for i in range(n_items):
        pat = [0]*n_items
        if widths[i] <= roll_length:
            pat[i] = int(roll_length // widths[i])
        else:
            pat[i] = 1 # Should not happen if data is valid
        patterns.append(pat)

    iter_count = 0
    max_iter = 50
    logs = []

    final_res = None

    while iter_count < max_iter:
        # Solve Master LP
        # Min sum(x) s.t. A x >= quantities
        # Scipy: Min c x s.t. -A x <= -quantities

        current_patterns = np.array(patterns).T # n_items x n_patterns
        n_patterns = len(patterns)
        c = np.ones(n_patterns)

        res = linprog(c, A_ub=-current_patterns, b_ub=-np.array(quantities), bounds=(0, None), method='highs')

        if not res.success:
            return {"error": "Master problem infeasible", "logs": logs}

        final_res = res

        # Duals (shadow prices)
        # For -Ax <= -b, duals are negative. pi = -duals
        duals = -res.ineqlin.marginals
        # Replace any negative zeros or small errors
        duals = np.maximum(duals, 0)

        # Subproblem: Knapsack
        # Maximize sum(duals[i] * a[i]) s.t. sum(widths[i] * a[i]) <= roll_length
        # Scipy milp minimizes c^T x, so we minimize -duals^T a

        c_sub = -duals

        # Constraints: 0 <= widths @ a <= roll_length
        A_sub = np.array([widths]) # 1 x n_items matrix
        b_l = np.array([0])
        b_u = np.array([roll_length])

        constraints = LinearConstraint(A_sub, b_l, b_u)
        integrality = np.ones(n_items) # All integer

        # Solve using HiGHS (via scipy.optimize.milp) - much faster than spawning CBC process
        res_sub = milp(c=c_sub, constraints=constraints, integrality=integrality)

        if not res_sub.success:
             logs.append(f"Subproblem failed: {res_sub.message}")
             break

        new_pattern_val = -res_sub.fun
        new_pattern = [int(round(x)) for x in res_sub.x]

        if new_pattern_val <= 1 + 1e-5:
            logs.append(f"Optimality reached. Max reduced cost val: {new_pattern_val:.4f} <= 1")
            break

        # Check if pattern already exists to avoid cycling (numerical issues)
        if any((np.array(new_pattern) == np.array(p)).all() for p in patterns):
            logs.append("Generated existing pattern. Stopping.")
            break

        patterns.append(new_pattern)
        logs.append(f"Iter {iter_count}: Added pattern {new_pattern} (Value: {new_pattern_val:.4f})")
        iter_count += 1

    return {
        "status": "Optimal",
        "objective": final_res.fun if final_res else 0,
        "patterns": patterns,
        "solution": final_res.x.tolist() if final_res else [],
        "logs": logs
    }
