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

    for i in range(n_scenarios):
        prob = probs[i]
        base_idx = 3 + i * 6
        # w1, w2 (sell) -> coeff -170*p, -150*p
        c[base_idx] = -sell_price[0] * prob
        c[base_idx+1] = -sell_price[1] * prob
        # y1, y2 (buy) -> coeff 238*p, 210*p
        c[base_idx+2] = buy_price[0] * prob
        c[base_idx+3] = buy_price[1] * prob
        # z1, z2 (beets) -> coeff -36*p, -10*p
        c[base_idx+4] = -sell_price[2] * prob
        c[base_idx+5] = -sell_price[3] * prob

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

    ub_idx = 1
    eq_idx = 0

    # Per Scenario Constraints
    for i, scen in enumerate(scenarios):
        yld = scen['yields'] # [yW, yC, yB]
        base_idx = 3 + i * 6

        # Wheat Balance: -yield*x1 - y1 + w1 <= -200
        A_ub[ub_idx, 0] = -yld[0]      # -yield*x1
        A_ub[ub_idx, base_idx] = 1.0     # +w1
        A_ub[ub_idx, base_idx+2] = -1.0  # -y1
        b_ub[ub_idx] = -demands[0]
        ub_idx += 1

        # Corn Balance: -yield*x2 - y2 + w2 <= -240
        A_ub[ub_idx, 1] = -yld[1]
        A_ub[ub_idx, base_idx+1] = 1.0
        A_ub[ub_idx, base_idx+3] = -1.0
        b_ub[ub_idx] = -demands[1]
        ub_idx += 1

        # Beets Balance (Produced = Sold Quota + Sold Excess)
        # yld[2]*x3 - z1 - z2 = 0
        A_eq[eq_idx, 2] = yld[2]
        A_eq[eq_idx, base_idx+4] = -1.0
        A_eq[eq_idx, base_idx+5] = -1.0
        b_eq[eq_idx] = 0.0
        eq_idx += 1

        # Quota Limit: z1 <= 6000
        A_ub[ub_idx, base_idx+4] = 1.0
        b_ub[ub_idx] = beets_quota
        ub_idx += 1

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
    scenario_profits = []

    sell_price = [170, 150, 36, 10]
    buy_price = [238, 210]

    for i in range(n_scenarios):
        base_idx = 3 + i * 6
        # w1, w2, y1, y2, z1, z2
        vars_s = all_x[base_idx:base_idx+6]
        revenue = vars_s[0]*sell_price[0] + vars_s[1]*sell_price[1] + vars_s[4]*sell_price[2] + vars_s[5]*sell_price[3]
        cost_purchase = vars_s[2]*buy_price[0] + vars_s[3]*buy_price[1]
        profit_s = revenue - cost_purchase - cost_planting
        scenario_profits.append(profit_s)

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
