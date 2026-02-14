## 2024-05-27 - [ColGen Subproblem Optimization]
**Learning:** For Column Generation where subproblems (Knapsack) are solved frequently, replacing `pulp` (which spawns subprocesses) with `scipy.optimize.milp` (which runs in-process via HiGHS) provides a significant speedup (~2.8x for n=20).
**Action:** Use native solvers like `scipy.optimize.milp` for small, frequent LP/IP subproblems instead of file-based interfaces.

## 2024-05-27 - [IP Search Strategy: BFS vs DFS]
**Learning:** Switching from BFS to DFS in a custom Branch and Bound implementation for Knapsack instances resulted in a ~4.5x slowdown (1.6s -> 7.2s). This suggests that for these instances, finding a feasible solution via DFS was not as critical as exploring the broader tree structure or the node ordering was suboptimal.
**Action:** Default to Best-First Search for B&B, or verify node ordering heuristics carefully before committing to DFS.
