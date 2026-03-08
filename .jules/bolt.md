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

## 2025-02-28 - O(1) Set Lookup vs O(N) Iteration checking in Column Generation Loop
**Learning:** In the Column Generation solver's iteration loop, repeatedly checking if a newly generated pattern exists in the list of previously generated patterns using array comparisons (`if any((np.array(new_pattern) == np.array(p)).all() for p in patterns)`) is extremely slow `O(N)` since N is constantly increasing on each iteration. Storing patterns as tuples in a `set` and doing `tuple(new_pattern) in patterns_set` reduced this complexity to `O(1)`, resulting in a measurable performance increase.
**Action:** Always use sets and tuple structures when performing lookups over frequently mutated collections to preserve `O(1)` time complexity.

## 2025-03-03 - O(N^2) Array Recreation in Loops
**Learning:** In the Column Generation solver, rebuilding the `A_ub` constraint matrix on every iteration by converting a growing list of lists via `np.array(patterns).T` causes severe `O(N^2)` memory reallocation overhead.
**Action:** When a constraint matrix or an objective vector grows incrementally inside an optimization loop, pre-allocate or incrementally update existing NumPy arrays using `np.hstack` or `np.append` instead of parsing an entire Python list from scratch on every iteration. Also, extract constant attributes (like bounds) out of the loop.

## 2025-03-05 - O(N^2) Array Reallocation with np.hstack in tight loops
**Learning:** Even when avoiding Python lists, using `np.hstack` or `np.append` incrementally inside a loop still causes `O(N^2)` memory reallocation because NumPy allocates a completely new array under the hood for every call. For small inner loops like the Column Generation solver, this is measurably slower (e.g., 4-9x slower depending on scale).
**Action:** Always pre-allocate NumPy arrays to their maximum possible size before entering the iteration loop, and use indexing/slicing (e.g., `matrix[:, current_cols] = ...`) to insert elements. This achieves true `O(1)` amortized memory allocation per iteration.

## 2025-03-04 - [API Payload Compression: GZip Middleware for Base64 Images]
**Learning:** Large JSON responses containing base64-encoded PNG strings generated by Matplotlib can be surprisingly highly compressible (reducing size by ~25-30% from 67KB to 48KB in my testing). Relying on the client to download large payloads uncompressed wastes bandwidth and slows down network transfer.
**Action:** Use `GZipMiddleware` in FastAPI (built-in via Starlette) configured with a `minimum_size` (e.g., 1000 bytes) to automatically compress JSON responses containing large strings like base64 plots, thereby saving network overhead.

## 2025-03-05 - [Vectorizing Iterative Array Calculations]
**Learning:** In stochastic programming models (or any solver with a large `n_scenarios` parameter), building objective coefficient arrays or calculating per-scenario results using Python `for` loops is severely unoptimized. Our benchmarks showed Python loops taking ~0.2s for 100k scenarios, while NumPy vectorized operations (`probs[:, np.newaxis] * scenario_coeffs`) and 2D `.reshape()` dot products took ~0.01s (a 20x speedup).
**Action:** When working with parameter matrices across many scenarios, always replace Python iteration loops with NumPy broadcasting, `.reshape()`, and `.dot()` operations to process all scenarios simultaneously.

## 2025-03-08 - [Stochastic Solver: Matrix Vectorization]
**Learning:** In the two-stage stochastic LP solver, generating constraint matrices (`A_ub`, `A_eq`) by iterating over thousands of scenarios in a Python loop is a major bottleneck (taking >6s for 2000 scenarios).
**Action:** Replaced the Python loop with vectorized NumPy advanced indexing (e.g., `A_ub[wheat_ub_idx, base_indices] = 1.0`), which populates all scenario constraints simultaneously. This optimization reduces the constraint generation time by ~25x (from >6s to ~0.2s for large scenarios) while maintaining perfect mathematical equivalence. Always use vectorized array assignments instead of `for` loops when constructing large block-diagonal or patterned matrices.
