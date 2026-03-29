import numpy as np
from scipy.optimize import linprog
import scipy.sparse as sp
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io
import base64

def solve_stochastic(total_land, scenarios):
    """
    Solves the Farmer's problem (Two-Stage Stochastic LP).
    Maximize Expected Profit.
    scenarios: list of dict with 'probability' and 'yields' (list of 3 floats: Wheat, Corn, Beets)
    """
    # Costs per acre
    planting_costs = np.array([150, 230, 260], dtype=float) # Wheat, Corn, Beets

    # Selling prices
    sell_price = np.array([170, 150, 36, 10], dtype=float) # Wheat, Corn, Beets (quota), Beets (excess)
    # Purchase prices
    buy_price = np.array([238, 210], dtype=float) # Wheat, Corn

    # Demands (feeding requirements)
    demands = np.array([200, 240], dtype=float) # Wheat, Corn

    # Quota for Beets
    beets_quota = 6000.0

    n_scenarios = len(scenarios)
    # Optimization: Use np.fromiter with a pre-calculated count instead of a list comprehension and np.array
    # This avoids intermediate Python list creation and improves speed and memory efficiency for large scenario counts.
    probs = np.fromiter((s['probability'] for s in scenarios), dtype=float, count=n_scenarios)

    # Variables:
    # x (3): planted acres
    # For each scenario s:
    #   w_s (2): sold wheat, corn
    #   y_s (2): purchased wheat, corn
    #   z_s (2): sold beets (quota, excess)
    # Total per scenario: 2+2+2 = 6 vars.
    # Total vars: 3 + 6*S

    num_vars = 3 + 6 * n_scenarios

    # Objective: Minimize -Expected Profit
    # Profit = Sum_s p_s * [ (170 w1 + 150 w2 + 36 z1 + 10 z2) - (238 y1 + 210 y2) ] - (150 x1 + 230 x2 + 260 x3)
    # Coeffs for x: 150, 230, 260 (positive because we minimize cost - revenue)
    c = np.zeros(num_vars)
    c[0:3] = planting_costs

    # Optimization: Use NumPy broadcasting to calculate objective coefficients for all scenarios simultaneously,
    # completely eliminating the O(N_SCENARIOS) Python for-loop overhead.
    scenario_coeffs = np.array([
        -sell_price[0], -sell_price[1],
        buy_price[0], buy_price[1],
        -sell_price[2], -sell_price[3]
    ])
    # Optimization: Use .ravel() instead of .flatten() to avoid redundant memory allocation and copying overhead.
    c[3:] = (probs[:, np.newaxis] * scenario_coeffs).ravel()

    # Optimization: Pre-allocate numpy arrays for sparse matrices instead of appending to lists.
    # We construct A_ub and A_eq as scipy.sparse.coo_matrix to vastly improve memory footprint
    # and solve time for large scenario counts since the constraint matrices are extremely sparse.
    n_ub_constraints = 1 + 3 * n_scenarios
    n_eq_constraints = n_scenarios

    # A_ub Nonzeros: 3 (land) + S*3 (wheat) + S*3 (corn) + S*1 (quota) = 3 + 7*S
    nnz_ub = 3 + 7 * n_scenarios
    rows_ub = np.zeros(nnz_ub, dtype=int)
    cols_ub = np.zeros(nnz_ub, dtype=int)
    vals_ub = np.zeros(nnz_ub)
    b_ub = np.zeros(n_ub_constraints)

    # 1. Land constraint: x1 + x2 + x3 <= total_land
    rows_ub[0:3] = 0
    cols_ub[0:3] = [0, 1, 2]
    vals_ub[0:3] = 1.0
    b_ub[0] = total_land

    idx = 3
    # Optimization: Use np.fromiter with a pre-calculated count instead of a list comprehension and np.array
    # This avoids intermediate Python list creation and is measurably faster (~20-30%) for large scenario counts.
    ylds = np.fromiter((y for s in scenarios for y in s['yields']), dtype=float, count=n_scenarios * 3).reshape(n_scenarios, 3)
    base_indices = 3 + np.arange(n_scenarios) * 6

    # --- Wheat Constraints (ub_idx: 1, 4, 7...) ---
    wheat_ub_idx = 1 + np.arange(n_scenarios) * 3
    rows_ub[idx:idx + 3*n_scenarios] = np.repeat(wheat_ub_idx, 3)
    # Optimization: Use .ravel() instead of .flatten() to return a contiguous view and prevent redundant deep copies.
    cols_ub[idx:idx + 3*n_scenarios] = np.column_stack((np.zeros(n_scenarios, dtype=int), base_indices, base_indices + 2)).ravel()
    vals_ub[idx:idx + 3*n_scenarios] = np.column_stack((-ylds[:, 0], np.ones(n_scenarios), np.full(n_scenarios, -1.0))).ravel()
    b_ub[wheat_ub_idx] = -demands[0]
    idx += 3*n_scenarios

    # --- Corn Constraints (ub_idx: 2, 5, 8...) ---
    corn_ub_idx = 2 + np.arange(n_scenarios) * 3
    rows_ub[idx:idx + 3*n_scenarios] = np.repeat(corn_ub_idx, 3)
    cols_ub[idx:idx + 3*n_scenarios] = np.column_stack((np.ones(n_scenarios, dtype=int), base_indices + 1, base_indices + 3)).ravel()
    vals_ub[idx:idx + 3*n_scenarios] = np.column_stack((-ylds[:, 1], np.ones(n_scenarios), np.full(n_scenarios, -1.0))).ravel()
    b_ub[corn_ub_idx] = -demands[1]
    idx += 3*n_scenarios

    # --- Quota Limit Constraints (ub_idx: 3, 6, 9...) ---
    quota_ub_idx = 3 + np.arange(n_scenarios) * 3
    rows_ub[idx:idx + n_scenarios] = quota_ub_idx
    cols_ub[idx:idx + n_scenarios] = base_indices + 4
    vals_ub[idx:idx + n_scenarios] = np.ones(n_scenarios)
    b_ub[quota_ub_idx] = beets_quota

    A_ub = sp.coo_matrix((vals_ub, (rows_ub, cols_ub)), shape=(n_ub_constraints, num_vars))

    # --- Beets Balance Constraints (eq_idx: 0, 1, 2...) ---
    eq_idx = np.arange(n_scenarios)
    rows_eq = np.repeat(eq_idx, 3)
    cols_eq = np.column_stack((np.full(n_scenarios, 2, dtype=int), base_indices + 4, base_indices + 5)).ravel()
    vals_eq = np.column_stack((ylds[:, 2], np.full(n_scenarios, -1.0), np.full(n_scenarios, -1.0))).ravel()
    b_eq = np.zeros(n_eq_constraints)

    A_eq = sp.coo_matrix((vals_eq, (rows_eq, cols_eq)), shape=(n_eq_constraints, num_vars))

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method='highs')

    img_b64 = None
    if res.success:
        img_b64 = plot_stochastic(res.x[0:3], -res.fun, scenarios, probs, res.x, n_scenarios)

    return {
        "success": res.success,
        "x": res.x[0:3].tolist() if res.x is not None else None,
        "expected_profit": -res.fun if res.success else None,
        "plot": img_b64
    }

def plot_stochastic(acres, profit, scenarios, probs, all_x, n_scenarios):
    # Use Matplotlib Object-Oriented Interface for thread safety and performance
    fig = Figure(figsize=(10, 5))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    # Plot 1: Acres Allocation
    crops = ['Wheat', 'Corn', 'Beets']
    ax1.bar(crops, acres, color=['gold', 'orange', 'purple'])
    ax1.set_title('Acres Planted')
    ax1.set_ylabel('Acres')

    # Plot 2: Profit Distribution (Scenario Profits)
    # Calculate profit per scenario
    # Profit_s = Revenue_s - Cost_Planting
    cost_planting = np.dot(acres, [150, 230, 260])
    # Optimization: Reshape all_x into a 2D matrix (n_scenarios x 6) and use vectorized operations
    # and dot products to calculate scenario profits instantly, replacing the slow Python list appending loop.
    sell_price_arr = np.array([170, 150, 36, 10])
    buy_price_arr = np.array([238, 210])

    scenario_vars = all_x[3:3 + n_scenarios * 6].reshape(n_scenarios, 6)
    revenues = np.dot(scenario_vars[:, [0, 1, 4, 5]], sell_price_arr)
    cost_purchases = np.dot(scenario_vars[:, [2, 3]], buy_price_arr)

    scenario_profits = revenues - cost_purchases - cost_planting

    # Optimization: Don't plot individual bars if there are too many scenarios.
    # Plotting thousands of bars is extremely slow (e.g., ~9s for 1000 bars) and visually unreadable.
    # Instead, plot a histogram to show the distribution of profits.
    if n_scenarios <= 50:
        ax2.bar([s['name'] for s in scenarios], scenario_profits, color='skyblue')
        ax2.axhline(profit, color='red', linestyle='--', label=f'Exp: {profit:.0f}')
    else:
        ax2.hist(scenario_profits, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
        ax2.set_xlabel('Profit')
        ax2.set_ylabel('Frequency')
        ax2.axvline(profit, color='red', linestyle='--', label=f'Exp: {profit:.0f}')

    ax2.set_title('Profit per Scenario')
    ax2.legend()

    fig.tight_layout()
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)

    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    # No need to explicitly close fig as it is garbage collected
    return img_str
