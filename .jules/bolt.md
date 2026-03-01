## 2024-05-27 - [ColGen Subproblem Optimization]
**Learning:** For Column Generation where subproblems (Knapsack) are solved frequently, replacing `pulp` (which spawns subprocesses) with `scipy.optimize.milp` (which runs in-process via HiGHS) provides a significant speedup (~2.8x for n=20).
**Action:** Use native solvers like `scipy.optimize.milp` for small, frequent LP/IP subproblems instead of file-based interfaces.

## 2024-05-27 - [IP Search Strategy: BFS vs DFS]
**Learning:** Switching from BFS to DFS in a custom Branch and Bound implementation for Knapsack instances resulted in a ~4.5x slowdown (1.6s -> 7.2s). This suggests that for these instances, finding a feasible solution via DFS was not as critical as exploring the broader tree structure or the node ordering was suboptimal.
**Action:** Default to Best-First Search for B&B, or verify node ordering heuristics carefully before committing to DFS.

## 2024-05-27 - [Branching Heuristic: Most Fractional vs First Fractional]
**Learning:** "Most Fractional" branching (picking variable closest to 0.5) provided no benefit for pure Knapsack problems (neutral performance) because the LP relaxation typically yields only one fractional variable. However, for General MIPs with multiple constraints, it reduced node count by ~37% and time by ~28%.
**Action:** Use "Most Fractional" branching for general purpose solvers, but don't expect magic on single-constraint problems.

## 2025-05-27 - [Matplotlib Performance: Stateful vs OO]
**Learning:** Using `matplotlib.pyplot` (stateful) for plot generation in the backend is ~25% slower (0.22s vs 0.16s for small trees) than using the Object-Oriented interface (`Figure`, `FigureCanvasAgg`). The stateful interface also risks thread-safety issues in a web server context.
**Action:** Always use the `Figure` and `FigureCanvasAgg` classes directly for backend image generation, avoiding `plt.figure()` and `plt.savefig()`.

## 2025-02-28 - Numpy Pre-allocation for Constraint Matrices
**Learning:** In the stochastic solver, dynamically appending constraint rows and right-hand side values to standard Python lists and then letting Scipy convert them to Numpy arrays incurs an unnecessary memory reallocation overhead inside loops (O(N)).
**Action:** When building large constraint systems across many scenarios or iterations, pre-allocate Numpy arrays with zeros using the known constraint size, and update the indices directly. This avoids memory reallocation overhead and reduces execution time.

## 2025-02-28 - Pre-computing Broadcasted Numpy Matrices in Inner Loops
**Learning:** Inside the Lagrangian solver's inner iteration loop, computing `costs[:, j] - lambdas` for each column sequentially involves repeated memory allocation and array subtraction. Pre-computing the entire matrix difference outside the inner loop using Numpy broadcasting (`costs - lambdas[:, np.newaxis]`) eliminates these redundant operations and yields measurable execution time savings.
**Action:** Always pre-compute vector/matrix operations using broadcasting outside of inner loops when possible, rather than slicing and computing sequentially inside the loop.
