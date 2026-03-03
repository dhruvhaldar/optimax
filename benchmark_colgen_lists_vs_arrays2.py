import time
import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint

def solve_cutting_stock_orig(roll_length, demands):
    widths = [d[0] for d in demands]
    quantities = [d[1] for d in demands]
    n_items = len(widths)

    patterns = []
    patterns_set = set()
    for i in range(n_items):
        pat = [0]*n_items
        if widths[i] <= roll_length:
            pat[i] = int(roll_length // widths[i])
        else:
            pat[i] = 1
        patterns.append(pat)
        patterns_set.add(tuple(pat))

    iter_count = 0
    max_iter = 50
    final_res = None

    A_sub = np.array([widths])
    b_l = np.array([0])
    b_u = np.array([roll_length])
    constraints = LinearConstraint(A_sub, b_l, b_u)
    integrality = np.ones(n_items)
    quantities_arr = -np.array(quantities)

    while iter_count < max_iter:
        current_patterns = np.array(patterns).T
        n_patterns = len(patterns)
        c = np.ones(n_patterns)

        res = linprog(c, A_ub=-current_patterns, b_ub=quantities_arr, bounds=(0, None), method='highs')

        if not res.success: break
        final_res = res
        duals = -res.ineqlin.marginals
        duals = np.maximum(duals, 0)

        c_sub = -duals
        res_sub = milp(c=c_sub, constraints=constraints, integrality=integrality)

        if not res_sub.success: break

        new_pattern_val = -res_sub.fun
        if new_pattern_val <= 1 + 1e-5: break

        new_pattern = np.rint(res_sub.x).astype(int).tolist()
        new_pattern_tuple = tuple(new_pattern)

        if new_pattern_tuple in patterns_set: break

        patterns.append(new_pattern)
        patterns_set.add(new_pattern_tuple)
        iter_count += 1
    return final_res

def solve_cutting_stock_opt(roll_length, demands):
    widths = [d[0] for d in demands]
    quantities = [d[1] for d in demands]
    n_items = len(widths)

    patterns = []
    patterns_set = set()
    for i in range(n_items):
        pat = [0]*n_items
        if widths[i] <= roll_length:
            pat[i] = int(roll_length // widths[i])
        else:
            pat[i] = 1
        patterns.append(pat)
        patterns_set.add(tuple(pat))

    iter_count = 0
    max_iter = 50
    final_res = None

    A_sub = np.array([widths])
    b_l = np.array([0])
    b_u = np.array([roll_length])
    constraints = LinearConstraint(A_sub, b_l, b_u)
    integrality = np.ones(n_items)
    quantities_arr = -np.array(quantities)

    current_patterns_neg = -np.array(patterns).T
    c = np.ones(len(patterns))
    # use pre-allocated bounds object to avoid rebuilding
    bounds = (0, None)

    while iter_count < max_iter:
        res = linprog(c, A_ub=current_patterns_neg, b_ub=quantities_arr, bounds=bounds, method='highs')
        if not res.success: break
        final_res = res

        duals = -res.ineqlin.marginals
        duals = np.maximum(duals, 0)
        c_sub = -duals

        res_sub = milp(c=c_sub, constraints=constraints, integrality=integrality)
        if not res_sub.success: break

        new_pattern_val = -res_sub.fun
        if new_pattern_val <= 1 + 1e-5: break

        new_pattern = np.rint(res_sub.x).astype(int)
        new_pattern_tuple = tuple(new_pattern.tolist())
        if new_pattern_tuple in patterns_set: break

        patterns.append(new_pattern.tolist())
        patterns_set.add(new_pattern_tuple)

        current_patterns_neg = np.hstack((current_patterns_neg, -new_pattern.reshape(-1, 1)))
        c = np.append(c, 1)

        iter_count += 1
    return final_res

roll_length = 100
demands = [(22, 100), (42, 50), (52, 70), (53, 30)]

start = time.time()
for _ in range(100):
    solve_cutting_stock_orig(roll_length, demands)
end = time.time()
print(f"Colgen original: {end - start:.4f}s")

start = time.time()
for _ in range(100):
    solve_cutting_stock_opt(roll_length, demands)
end = time.time()
print(f"Colgen optimized: {end - start:.4f}s")
