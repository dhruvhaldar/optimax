import numpy as np
from scipy.optimize import linprog
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
    probs = np.array([s['probability'] for s in scenarios], dtype=float)

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
    c[3:] = (probs[:, np.newaxis] * scenario_coeffs).flatten()

    # Optimization: Pre-allocate numpy arrays for constraints instead of appending to lists.
    # This prevents O(N) memory reallocations inside the loop and significantly speeds up matrix creation.
    n_ub_constraints = 1 + 3 * n_scenarios
    A_ub = np.zeros((n_ub_constraints, num_vars))
    b_ub = np.zeros(n_ub_constraints)

    n_eq_constraints = n_scenarios
    A_eq = np.zeros((n_eq_constraints, num_vars))
    b_eq = np.zeros(n_eq_constraints)

    # 1. Land constraint: x1 + x2 + x3 <= total_land
    A_ub[0, 0:3] = 1.0
    b_ub[0] = total_land

    # Optimization: Use NumPy advanced indexing to calculate all scenario constraints simultaneously.
    # This completely eliminates the slow O(N_SCENARIOS) Python for-loop and dramatically speeds up constraint generation.
    ylds = np.array([s['yields'] for s in scenarios]) # Shape (n_scenarios, 3)
    base_indices = 3 + np.arange(n_scenarios) * 6

    # --- Wheat Constraints (ub_idx: 1, 4, 7...) ---
    wheat_ub_idx = 1 + np.arange(n_scenarios) * 3
    A_ub[wheat_ub_idx, 0] = -ylds[:, 0]               # -yield*x1
    A_ub[wheat_ub_idx, base_indices] = 1.0            # +w1
    A_ub[wheat_ub_idx, base_indices + 2] = -1.0       # -y1
    b_ub[wheat_ub_idx] = -demands[0]

    # --- Corn Constraints (ub_idx: 2, 5, 8...) ---
    corn_ub_idx = 2 + np.arange(n_scenarios) * 3
    A_ub[corn_ub_idx, 1] = -ylds[:, 1]                # -yield*x2
    A_ub[corn_ub_idx, base_indices + 1] = 1.0         # +w2
    A_ub[corn_ub_idx, base_indices + 3] = -1.0        # -y2
    b_ub[corn_ub_idx] = -demands[1]

    # --- Beets Balance Constraints (eq_idx: 0, 1, 2...) ---
    eq_idx = np.arange(n_scenarios)
    A_eq[eq_idx, 2] = ylds[:, 2]                      # yield*x3
    A_eq[eq_idx, base_indices + 4] = -1.0             # -z1
    A_eq[eq_idx, base_indices + 5] = -1.0             # -z2
    b_eq[eq_idx] = 0.0

    # --- Quota Limit Constraints (ub_idx: 3, 6, 9...) ---
    quota_ub_idx = 3 + np.arange(n_scenarios) * 3
    A_ub[quota_ub_idx, base_indices + 4] = 1.0        # z1
    b_ub[quota_ub_idx] = beets_quota

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

    ax2.bar([s['name'] for s in scenarios], scenario_profits, color='skyblue')
    ax2.axhline(profit, color='red', linestyle='--', label=f'Exp: {profit:.0f}')
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
