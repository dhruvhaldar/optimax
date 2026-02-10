import numpy as np
import pulp
import matplotlib.pyplot as plt
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
            prob = pulp.LpProblem(f"Agent_{j}", pulp.LpMaximize)
            x_vars = [pulp.LpVariable(f"x_{i}_{j}", 0, 1, cat="Integer") for i in range(n_tasks)]

            # Objective coeffs
            coeffs = lambdas - costs[:, j]
            prob += pulp.lpSum([coeffs[i] * x_vars[i] for i in range(n_tasks)])

            # Constraint
            prob += pulp.lpSum([weights[i, j] * x_vars[i] for i in range(n_tasks)]) <= capacities[j]

            prob.solve(pulp.PULP_CBC_CMD(msg=0))

            if pulp.value(prob.objective) is not None:
                subproblem_obj_sum += pulp.value(prob.objective)
                for i in range(n_tasks):
                    current_x[i, j] = x_vars[i].varValue

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
    plt.figure(figsize=(6, 4))
    plt.plot(history, marker='o')
    plt.title("Lagrangian Lower Bound Convergence")
    plt.xlabel("Iteration")
    plt.ylabel("Lower Bound")
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_str
