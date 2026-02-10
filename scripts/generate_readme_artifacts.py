import sys
import os
import base64
import matplotlib

# Set backend to Agg before importing pyplot via solvers
matplotlib.use('Agg')

# Add root to path
sys.path.append(os.getcwd())

from api.solvers import lp, ip, lagrangian, stochastic

# Create assets dir
os.makedirs("assets", exist_ok=True)

def save_b64(b64_str, filename):
    if not b64_str:
        print(f"No plot data for {filename}")
        return
    with open(f"assets/{filename}", "wb") as f:
        f.write(base64.b64decode(b64_str))
    print(f"Saved {filename}")

# LP
print("Generating LP artifact...")
c = [3, 2]
A = [[2, 1], [1, 1], [1, 0]]
b = [100, 80, 40]
res = lp.solve_lp(c, A, b, maximize=True)
save_b64(res.get('plot'), "lp.png")

# IP
print("Generating IP artifact...")
c_ip = [5, 8]
A_ip = [[1, 1], [5, 9]]
b_ip = [6, 45]
res_ip = ip.solve_ip(c_ip, A_ip, b_ip, maximize=True)
save_b64(res_ip.get('tree_plot'), "ip.png")

# Lagrangian
print("Generating Lagrangian artifact...")
costs = [[10, 20], [15, 10], [5, 5]]
weights = [[2, 5], [3, 2], [1, 1]]
caps = [5, 5]
res_lag = lagrangian.solve_lagrangian(costs, weights, caps)
save_b64(res_lag.get('plot'), "lagrangian.png")

# Stochastic
print("Generating Stochastic artifact...")
scenarios = [
    {"name": "Good", "probability": 0.33, "yields": [3.0, 3.6, 24.0]},
    {"name": "Average", "probability": 0.33, "yields": [2.5, 3.0, 20.0]},
    {"name": "Bad", "probability": 0.34, "yields": [2.0, 2.4, 16.0]}
]
res_stoch = stochastic.solve_stochastic(500, scenarios)
save_b64(res_stoch.get('plot'), "stochastic.png")

print("Done.")
