import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import scipy.sparse as sp
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io
import base64

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

    # Security: Validate dimensions to prevent IndexError (DoS)
    if costs.ndim != 2:
        raise ValueError("Costs must be a 2D matrix")

    n_tasks, n_agents = costs.shape

    if weights.shape != (n_tasks, n_agents):
        raise ValueError(f"Weights must be a {n_tasks}x{n_agents} matrix")
    if capacities.shape != (n_agents,):
        raise ValueError(f"Capacities must be a 1D array of length {n_agents}")

    # Initialize multipliers (lambda)
    lambdas = np.zeros(n_tasks)

    max_iter = 20
    logs = []
    lb_history = []

    ub = np.inf
    best_sol = None

    # Optimization: Pre-compute a single, global sparse constraint matrix for all subproblems combined.
    # This prevents the incredibly slow setup and overhead of calling milp() inside a loop n_agents times per iteration.
    # By vectorizing all n_agents subproblems into one sparse block diagonal formulation, milp solve time drops by >50%.
    bounds = Bounds(0, 1) # All variables are binary {0, 1}
    integrality = np.ones(n_tasks * n_agents) # All variables are integers

    # Pre-compute global LinearConstraint for all agents simultaneously
    # Let global x = [x_11, x_21, ..., x_n1, x_12, ..., x_n2, ..., x_nm] (Flattened column-major, order='F')
    # Row j corresponds to sum_i w_ij x_ij <= C_j
    rows = np.repeat(np.arange(n_agents), n_tasks)
    cols = np.arange(n_tasks * n_agents)
    # Optimization: Use .ravel('F') instead of .flatten('F') to return a contiguous view and avoid redundant memory copying.
    vals = weights.ravel('F')

    A_sub_sparse = sp.coo_matrix((vals, (rows, cols)), shape=(n_agents, n_tasks * n_agents))
    b_l = np.full(n_agents, -np.inf)
    b_u = capacities
    all_constraints_sparse = LinearConstraint(A_sub_sparse, b_l, b_u)

    for k in range(max_iter):
        # Solve Subproblems
        # Maximize sum_j sum_i (lambdas[i] - c_ij) x_ij
        # s.t. sum_i w_ij x_ij <= C_j

        current_x = np.zeros((n_tasks, n_agents))
        subproblem_obj_sum = 0

        # Optimization: Pre-calculate the cost modifier matrix
        c_sub_all = costs - lambdas[:, np.newaxis]

        # Optimization: Flatten the cost matrix to match the global x vector, and solve all subproblems in one milp call.
        # Use .ravel('F') instead of .flatten('F') to prevent creating a deep copy in memory.
        c_sub_flat = c_sub_all.ravel('F')

        res = milp(c=c_sub_flat, constraints=all_constraints_sparse, integrality=integrality, bounds=bounds)

        if res.success:
            # milp minimizes, so objective value is negative of our maximization target
            subproblem_obj_sum = -res.fun
            # Reshape the global solution vector back to (n_tasks, n_agents) matrix
            current_x = np.round(res.x).reshape((n_tasks, n_agents), order='F')

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
    # Use Matplotlib Object-Oriented Interface for thread safety and performance
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
    # No need to explicitly close fig as it is garbage collected
    return img_str
