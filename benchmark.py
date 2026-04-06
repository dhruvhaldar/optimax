import numpy as np
import time

n_scenarios = 100000
base_indices = 3 + np.arange(n_scenarios) * 6
ylds = np.random.rand(n_scenarios, 3)

start = time.time()
for _ in range(100):
    a = np.column_stack((np.zeros(n_scenarios, dtype=int), base_indices, base_indices + 2)).ravel()
    b = np.column_stack((-ylds[:, 0], np.ones(n_scenarios), np.full(n_scenarios, -1.0))).ravel()
print(f"column_stack time: {time.time() - start:.4f}s")

start = time.time()
for _ in range(100):
    a = np.empty(3 * n_scenarios, dtype=int)
    a[0::3] = 0
    a[1::3] = base_indices
    a[2::3] = base_indices + 2
    b = np.empty(3 * n_scenarios, dtype=float)
    b[0::3] = -ylds[:, 0]
    b[1::3] = 1.0
    b[2::3] = -1.0
print(f"strided slice time: {time.time() - start:.4f}s")
