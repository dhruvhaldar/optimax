import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt
import networkx as nx
import io
import base64

class Node:
    def __init__(self, id, level, parent_id, decision, bounds):
        self.id = id
        self.level = level
        self.parent_id = parent_id
        self.decision = decision # e.g. "x1 <= 3"
        self.bounds = bounds # List of (min, max) for each var
        self.solution = None
        self.value = -np.inf
        self.status = "open" # open, pruned, integer, infeasible, branched

def solve_ip(c, A_ub, b_ub, maximize=True, max_nodes=1000):
    """
    Solves Integer Programming problem using Branch and Bound.
    Maximize c^T x s.t. A_ub x <= b_ub, x >= 0, integer.
    """
    c = np.array(c)
    A_ub = np.array(A_ub)
    b_ub = np.array(b_ub)

    # Minimize -c for maximization
    c_lp = -c if maximize else c

    n_vars = len(c)
    initial_bounds = [(0, None)] * n_vars

    nodes = []
    queue = []

    root = Node(0, 0, None, "Root", initial_bounds)
    nodes.append(root)
    queue.append(root)

    best_solution = None
    best_value = -np.inf if maximize else np.inf

    node_counter = 0
    processed_nodes = 0
    limit_reached = False

    while queue:
        if processed_nodes >= max_nodes:
            limit_reached = True
            break

        processed_nodes += 1
        current_node = queue.pop(0) # BFS

        # Solve LP relaxation
        res = linprog(c_lp, A_ub=A_ub, b_ub=b_ub, bounds=current_node.bounds, method='highs')

        if not res.success:
            current_node.status = "infeasible"
            current_node.value = -np.inf if maximize else np.inf
            continue

        val = -res.fun if maximize else res.fun
        current_node.value = val
        current_node.solution = res.x

        # Pruning by bound (if worst than best solution found so far)
        # For maximization: if val <= best_value, prune.
        # But for float, use tolerance.
        if maximize and val < best_value - 1e-6:
             current_node.status = "pruned"
             continue
        if not maximize and val > best_value + 1e-6:
             current_node.status = "pruned"
             continue

        # Check if integer
        is_integer = np.allclose(res.x, np.round(res.x), atol=1e-5)

        if is_integer:
            current_node.status = "integer"
            if (maximize and val > best_value) or (not maximize and val < best_value):
                best_value = val
                best_solution = res.x
        else:
            # Branch
            # Find first non-integer variable
            idx = -1
            for i, x_val in enumerate(res.x):
                if not np.isclose(x_val, round(x_val), atol=1e-5):
                    idx = i
                    break

            if idx != -1:
                current_node.status = "branched"
                val_floor = int(np.floor(res.x[idx]))
                val_ceil = int(np.ceil(res.x[idx]))

                # Left child: x[idx] <= floor
                left_bounds = current_node.bounds.copy()
                old_min, old_max = left_bounds[idx]
                new_max = val_floor
                if old_max is not None:
                    new_max = min(old_max, val_floor)
                left_bounds[idx] = (old_min, new_max)

                node_counter += 1
                left_node = Node(node_counter, current_node.level + 1, current_node.id, f"x{idx} <= {val_floor}", left_bounds)
                nodes.append(left_node)
                queue.append(left_node)

                # Right child: x[idx] >= ceil
                right_bounds = current_node.bounds.copy()
                old_min, old_max = right_bounds[idx]
                new_min = val_ceil
                if old_min is not None:
                    new_min = max(old_min, val_ceil) # Should be max(old_min, val_ceil)? Yes.
                else:
                    new_min = val_ceil
                right_bounds[idx] = (new_min, old_max)

                node_counter += 1
                right_node = Node(node_counter, current_node.level + 1, current_node.id, f"x{idx} >= {val_ceil}", right_bounds)
                nodes.append(right_node)
                queue.append(right_node)

    # Generate Tree Plot
    img_b64 = plot_tree(nodes)

    status = "Optimal"
    if limit_reached:
        status = "Limit Reached"
    elif best_solution is None:
        status = "Infeasible"

    return {
        "success": best_solution is not None,
        "status": status,
        "x": best_solution.tolist() if best_solution is not None else None,
        "fun": best_value,
        "tree_plot": img_b64
    }

def plot_tree(nodes):
    G = nx.DiGraph()
    node_map = {n.id: n for n in nodes}

    for node in nodes:
        G.add_node(node.id, subset=node.level)
        if node.parent_id is not None:
            G.add_edge(node.parent_id, node.id)

    pos = nx.multipartite_layout(G, subset_key="subset", align="horizontal")

    colors = []
    labels = {}
    for n_id in G.nodes():
        node = node_map[n_id]
        label = f"{node.id}\n{node.decision}"
        if node.value > -1e10: # Only show value if not -inf
             label += f"\nVal:{node.value:.1f}"

        if node.status == "integer":
            colors.append("#90EE90") # Light green
            label += "\n(INT)"
        elif node.status == "infeasible":
            colors.append("#F08080") # Light coral
            label += "\n(INF)"
        elif node.status == "branched":
            colors.append("#ADD8E6") # Light blue
        elif node.status == "pruned":
            colors.append("#D3D3D3") # Light gray
            label += "\n(Pruned)"
        else:
            colors.append("white")

        labels[n_id] = label

    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, labels=labels, node_color=colors, node_size=2000, font_size=8, node_shape="o", arrows=True)
    plt.title("Branch and Bound Tree")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_str
