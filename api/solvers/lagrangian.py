import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import io
import base64
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

def solve_lagrangian(costs, weights, capacities):
    """
    Solves Generalized Assignment Problem using Lagrangian Relaxation.
    Relaxing the assignment constraints: sum_j x_ij = 1.
    costs: n_tasks x n_agents (list of lists)
    weights: n_tasks x n_agents (list of lists)
    capacities: n_agents (list)
    """
    costs = np.array(costs)
    weights = np.array(weights)
    capacities = np.array(capacities)

    n_tasks, n_agents = costs.shape

    # Initialize multipliers (lambda)
    lambdas = np.zeros(n_tasks)

    max_iter = 20
    logs = []
    lb_history = []

    ub = np.inf
    best_sol = None

    # Simple heuristic to get initial UB?
    # Just solve as LP or simple greedy? Skip for now.

    for k in range(max_iter):
        # Solve Subproblems
        # Maximize sum_j sum_i (lambdas[i] - c_ij) x_ij
        # s.t. sum_i w_ij x_ij <= C_j

        current_x = np.zeros((n_tasks, n_agents))
        subproblem_obj_sum = 0

        for j in range(n_agents):
            # Maximize sum_i (lambdas[i] - c_ij) x_ij
            # Equivalent to Minimize sum_i (c_ij - lambdas[i]) x_ij
            c_sub = costs[:, j] - lambdas

            # Constraint: sum_i w_ij x_ij <= C_j
            # milp constraints: lb <= A_ub x <= ub
            # Here: -inf <= w^T x <= C_j
            A_sub = np.array([weights[:, j]]) # 1 x n_tasks matrix
            b_l = np.array([-np.inf])
            b_u = np.array([capacities[j]])

            constraints = LinearConstraint(A_sub, b_l, b_u)
            integrality = np.ones(n_tasks) # All variables are integers
            bounds = Bounds(0, 1) # All variables are binary {0, 1}

            res = milp(c=c_sub, constraints=constraints, integrality=integrality, bounds=bounds)

            if res.success:
                # milp minimizes, so objective value is negative of our maximization target
                subproblem_obj_sum += -res.fun
                current_x[:, j] = np.round(res.x) # milp returns float array, round to integer

        # LB = sum(lambdas) - Max ... = sum(lambdas) - subproblem_obj_sum
        current_lb = np.sum(lambdas) - subproblem_obj_sum
        lb_history.append(current_lb)

        # Subgradient: g_i = 1 - sum_j x_ij
        # If sum_j x_ij > 1, we assigned task to multiple agents. g_i < 0 => reduce lambda => reduce reward.
        # If sum_j x_ij = 0, we didn't assign. g_i > 0 => increase lambda => increase reward.
        g = 1 - np.sum(current_x, axis=1)

        # Check Primal Feasibility
        if np.all(g == 0):
            # Feasible
            cost = np.sum(current_x * costs)
            if cost < ub:
                ub = cost
                best_sol = current_x.copy()
            logs.append(f"Iter {k}: Feasible! LB={current_lb:.2f}, Cost={cost:.2f}")
        else:
            logs.append(f"Iter {k}: LB={current_lb:.2f}, Infeasibility norm={np.linalg.norm(g):.2f}")

        if np.linalg.norm(g) == 0:
            break

        # Step size
        # Simple diminishing step
        step = 10.0 / (k + 1)
        lambdas = lambdas + step * g

    img_b64 = plot_convergence(lb_history)

    return {
        "status": "Completed",
        "lb_history": lb_history,
        "ub": ub if ub != np.inf else None,
        "best_solution": best_sol.tolist() if best_sol is not None else None,
        "plot": img_b64,
        "logs": logs
    }

def plot_convergence(history):
    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)

    ax.plot(history, marker='o')
    ax.set_title("Lagrangian Lower Bound Convergence")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Lower Bound")
    ax.grid(True)

    buf = io.BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)

    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return img_str
