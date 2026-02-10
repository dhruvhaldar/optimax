import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt
import io
import base64

def solve_lp(c, A_ub, b_ub, bounds=None, maximize=False):
    """
    Solves a Linear Programming problem:
    Minimize: c^T * x
    Subject to: A_ub * x <= b_ub
                bounds
    """
    c = np.array(c)
    A_ub = np.array(A_ub)
    b_ub = np.array(b_ub)

    # Scipy linprog minimizes by default. If maximizing, negate c.
    c_solver = -c if maximize else c

    # Check if bounds are provided, else assume non-negative
    if bounds is None:
        bounds = [(0, None)] * len(c)

    res = linprog(c_solver, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    img_b64 = None
    if len(c) == 2 and res.success:
        try:
            img_b64 = plot_lp(c, A_ub, b_ub, res.x, maximize)
        except Exception as e:
            print(f"Plotting failed: {e}")

    return {
        "success": res.success,
        "message": res.message,
        "x": res.x.tolist() if res.x is not None else None,
        "fun": -res.fun if maximize else res.fun,
        "plot": img_b64
    }

def plot_lp(c, A_ub, b_ub, optimal_x, maximize):
    plt.figure(figsize=(6, 6))

    # Determine plot limits based on constraints and optimal solution
    # Simple heuristic: max of intercepts and optimal solution
    max_val = 0
    if optimal_x is not None:
        max_val = max(max_val, np.max(optimal_x))

    # Check intercepts
    for i in range(len(b_ub)):
        a1, a2 = A_ub[i]
        b = b_ub[i]
        if a1 > 0: max_val = max(max_val, b/a1)
        if a2 > 0: max_val = max(max_val, b/a2)

    limit = max(10, max_val * 1.2)
    x = np.linspace(0, limit, 400)

    # Plot constraints
    # a1*x + a2*y <= b
    y_min_feasible = np.zeros_like(x)
    y_max_feasible = np.full_like(x, limit)

    for i in range(len(b_ub)):
        a1, a2 = A_ub[i]
        b = b_ub[i]

        if a2 != 0:
            y = (b - a1 * x) / a2
            label = f'{a1}x1 + {a2}x2 <= {b}'
            plt.plot(x, y, label=label)

            # Update feasible region tracking (assuming <= constraints and a2 > 0)
            # This is a simplification for visualization
            if a2 > 0:
                y_max_feasible = np.minimum(y_max_feasible, y)
            elif a2 < 0:
                y_min_feasible = np.maximum(y_min_feasible, y)
        else:
            plt.axvline(b/a1, label=f'{a1}x1 <= {b}', color='gray', linestyle='--')
            # Handle vertical constraint for fill? Complex.

    # Shade feasible region (simplified)
    plt.fill_between(x, y_min_feasible, y_max_feasible, where=(y_max_feasible >= y_min_feasible), color='green', alpha=0.1)

    # Plot Objective Function at Optimal
    # Z = c1*x + c2*y => y = (Z - c1*x)/c2
    opt_val = np.dot(c, optimal_x)
    c1, c2 = c
    if c2 != 0:
        y_obj = (opt_val - c1 * x) / c2
        plt.plot(x, y_obj, 'r--', linewidth=2, label=f'Obj: {opt_val:.2f}')

    plt.plot(optimal_x[0], optimal_x[1], 'ro', markersize=8, label='Optimal')

    plt.xlim(0, limit)
    plt.ylim(0, limit)
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.title('LP Visualization')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_str
