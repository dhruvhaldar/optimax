import numpy as np
from scipy.optimize import linprog, milp, Bounds, LinearConstraint

def solve_cutting_stock(roll_length, demands):
    """
    Solves Cutting Stock problem using Column Generation.
    demands: list of (width, quantity)
    """
    widths = [d[0] for d in demands]
    quantities = [d[1] for d in demands]
    n_items = len(widths)

    # Security: Validate inputs to prevent ZeroDivisionError (DoS)
    for w in widths:
        if w <= 0:
            raise ValueError("Demand widths must be strictly positive")

    if roll_length <= 0:
        raise ValueError("Roll length must be strictly positive")

    # Security: Prevent Out-Of-Memory (OOM) DoS
    # roll_length determines the size of the DP array (O(W) memory).
    if roll_length > 100000:
        raise ValueError("Roll length exceeds maximum allowed size (100000)")

    # Initial patterns: One roll for each item type (identity matrix like)
    # Actually, a better initial basis is fitting as many of item i as possible
    patterns = []
    patterns_set = set() # O(1) lookup
    for i in range(n_items):
        pat = [0]*n_items
        if widths[i] <= roll_length:
            pat[i] = int(roll_length // widths[i])
        else:
            pat[i] = 1 # Should not happen if data is valid
        patterns.append(tuple(pat))
        patterns_set.add(tuple(pat))

    iter_count = 0
    max_iter = 50
    logs = []

    final_res = None

    # Constraints: 0 <= widths @ a <= roll_length
    # Convert capacities and weights to integers for DP
    W = int(roll_length)
    widths_int = np.array([int(w) for w in widths])

    # Pre-calculate the negative quantities array
    quantities_arr = -np.array(quantities)

    # Optimization: Pre-allocate numpy arrays for the constraint matrix (current_patterns_neg) and objective (c)
    # up to the maximum possible size (n_items + max_iter).
    # This prevents O(N^2) memory reallocation overhead from using np.hstack/np.append inside the tight loop.
    max_cols = n_items + max_iter
    current_patterns_neg = np.zeros((n_items, max_cols))
    initial_patterns = -np.array(patterns, dtype=float).T
    current_patterns_neg[:, :n_items] = initial_patterns
    c = np.zeros(max_cols)
    c[:n_items] = 1
    bounds = (0, None) # Pre-allocate bounds tuple

    # Optimization: Pre-allocate constraints for the unbounded knapsack subproblem
    # This completely eliminates SciPy setup overhead within the loop.
    A_sub = np.array([widths_int])
    sub_bounds = Bounds(0, np.inf)
    sub_integrality = np.ones(n_items)
    sub_constraints = LinearConstraint(A_sub, -np.inf, W)

    current_cols = n_items

    while iter_count < max_iter:
        # Solve Master LP
        # Min sum(x) s.t. A x >= quantities
        # Scipy: Min c x s.t. -A x <= -quantities

        # Slice the pre-allocated arrays up to the current number of columns
        res = linprog(c[:current_cols], A_ub=current_patterns_neg[:, :current_cols], b_ub=quantities_arr, bounds=bounds, method='highs')

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

        # Subproblem: Knapsack using MILP
        # Maximize sum(duals[i] * a[i]) s.t. sum(widths[i] * a[i]) <= roll_length
        # Unbounded knapsack
        # Optimization: Instead of a pure Python 1D DP array, we use scipy.optimize.milp
        # with pre-allocated LinearConstraints. For large `W` (e.g. 100,000), iterating
        # a Python list 100,000 times per iteration per item is dramatically slower
        # (~25s total) than a vectorized call to milp (~1.5s total).

        c_sub = -duals # minimize -duals^T a

        sub_res = milp(c=c_sub, constraints=sub_constraints, integrality=sub_integrality, bounds=sub_bounds)

        if not sub_res.success:
            logs.append("Subproblem failed.")
            break

        new_pattern_val = -sub_res.fun
        new_pattern_arr = np.rint(sub_res.x).astype(int)
        new_pattern_tuple = tuple(new_pattern_arr.tolist())

        if new_pattern_val <= 1 + 1e-5:
            logs.append(f"Optimality reached. Max reduced cost val: {new_pattern_val:.4f} <= 1")
            break

        # Check if pattern already exists to avoid cycling (numerical issues)
        if new_pattern_tuple in patterns_set:
            logs.append("Generated existing pattern. Stopping.")
            break

        patterns.append(new_pattern_tuple)
        patterns_set.add(new_pattern_tuple)

        # Optimization: Insert the new pattern into the pre-allocated arrays
        current_patterns_neg[:, current_cols] = -new_pattern_arr
        c[current_cols] = 1
        current_cols += 1

        logs.append(f"Iter {iter_count}: Added pattern {list(new_pattern_tuple)} (Value: {new_pattern_val:.4f})")
        iter_count += 1

    return {
        "status": "Optimal",
        "objective": final_res.fun if final_res else 0,
        "patterns": [list(p) for p in patterns],
        "solution": final_res.x.tolist() if final_res else [],
        "logs": logs
    }
