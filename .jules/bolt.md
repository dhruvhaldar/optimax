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

## 2025-03-09 - [Sparse Constraint Matrices in scipy.optimize.linprog]
**Learning:** For stochastic programming or any linear programming problem with large, mostly empty block-diagonal constraint matrices, constructing `A_ub` and `A_eq` as dense Numpy arrays leads to severe memory allocation overhead and dramatically increases the solve time for solvers like HiGHS. In our tests with 1000 scenarios, constructing dense constraint matrices took over 6 seconds just to set up and solve.
**Action:** When a constraint matrix is highly sparse, always directly construct `scipy.sparse.coo_matrix` instances using the vectorized `(data, (row, col))` format instead of a 2D dense array. SciPy's `linprog` handles these natively and efficiently, dropping solve time by nearly 40x in some cases.

## 2025-03-10 - [Matplotlib Bar Chart Scaling bottleneck]
**Learning:** Plotting thousands of individual bars in a bar chart using `ax.bar` in Matplotlib is incredibly slow. In the Stochastic solver, plotting profits for 1000 scenarios individually as bars took ~9.5 seconds, dominating the API response time.
**Action:** For large categorical datasets with numerous elements, never plot individual bars. Dynamically switch to `ax.hist` to plot data distribution (bins) instead, which brings rendering time from several seconds down to ~0.25s and generates a much more readable visual.

## 2025-03-12 - [Vectorized milp calls in Lagrangian Solver]
**Learning:** In the Lagrangian Relaxation solver, solving `N` separate `milp` subproblems in a loop per iteration introduces enormous overhead due to repeated SciPy setup and execution costs.
**Action:** When solving multiple independent subproblems with identical variable bounds and integrality constraints (like the Lagrangian agent assignments), concatenate them into a single global `scipy.optimize.milp` problem. Use `scipy.sparse.coo_matrix` to construct a block-diagonal constraint matrix to maintain sparsity, and solve the combined problem in one vectorized call. This reduces solver time significantly (e.g., >50% time reduction for 200 tasks and 40 agents).

## 2025-03-12 - [IP Search Strategy: Best-First Search vs DFS]
**Learning:** Re-visiting the Branch and Bound implementation for IP problems, I noticed that Depth-First Search (DFS) was measurably slower (taking ~2.1s for a 20-variable Knapsack instance) compared to exploring nodes with the best objective value first.
**Action:** Replaced the LIFO queue (`deque.pop()`) with a priority queue (`heapq`) based on the parent's relaxed objective value, essentially changing the search to Best-First Search. This prioritizes the most promising branches first, drastically reducing the total number of nodes evaluated before finding optimality or pruning, dropping execution time for the 20-var problem to ~1.2s.

## 2025-05-27 - [Class Instantiation in Tight Loops]
**Learning:** Defining and instantiating a class inline within a tight while loop (like in the B&B `solve_ip` algorithm) carries massive Python object creation overhead and severely slows down execution (e.g., from ~0.17s to ~15s for large problems).
**Action:** Always pre-define classes outside of tight loops, ideally at the module level.

## 2025-05-27 - [__slots__ for Performance]
**Learning:** Using `__slots__` in Python classes that are instantiated thousands of times (like `Node` in a Branch and Bound tree) prevents the creation of `__dict__` for each instance, saving memory and slightly improving attribute access speed. Combining this with moving class definitions out of the loop provided a massive speedup for the IP solver.
**Action:** When a class represents a data structure that will have many instances (e.g., tree nodes, solver results), explicitly define `__slots__` to optimize memory and performance.

## 2025-05-27 - [Custom DP vs Scipy MILP for Subproblems]
**Learning:** For Unbounded Knapsack subproblems with integer weights in Column Generation, a pure Python/NumPy 1D dynamic programming approach is significantly faster (~2.5x-3.5x) than invoking `scipy.optimize.milp`. The constant overhead of setting up the SciPy MILP solver on every column generation iteration drastically slows down the total execution time, overshadowing any benefit from HiGHS's actual solve speed for small instances.
**Action:** When solving simple, structured IP subproblems (like Knapsack) iteratively inside a larger optimization loop, replace general-purpose solvers like `scipy.optimize.milp` with custom, exact algorithms (e.g., Dynamic Programming for Knapsack with integer weights) to bypass solver setup overhead and dramatically improve loop performance.

## 2025-03-20 - [NumPy vs Python Lists in Tight Loops]
**Learning:** While NumPy is generally faster for vectorized operations, accessing and modifying individual elements of a NumPy array inside a tight Python loop (e.g., `dp[w] = new_val`) introduces significant boxing and unboxing overhead. In the ColGen unbounded knapsack DP algorithm, replacing `dp = np.zeros(W)` with a standard Python list `dp = [0.0] * W` resulted in a ~3-4x speedup.
**Action:** When an algorithm strictly requires sequential element-by-element iteration and updating in pure Python (where vectorization isn't possible, like DP with dependencies on previous elements in the same loop), use native Python lists instead of NumPy arrays.

## 2026-03-21 - [Vectorized milp vs Native Python Loops for Large Integer Constraints]
**Learning:** While custom dynamic programming is technically exact and theoretically faster than linear programming setup overhead for small integer knapsacks, executing 100,000 iterations of an inner loop natively in Python to populate a 1D DP list takes an extraordinarily long time (~25s) compared to executing a highly optimized C++ solver like HiGHS inside `scipy.optimize.milp` (~1.5s). Memory suggested DP was faster, but this was a premature optimization that did not account for Python's raw loop execution speed vs compiled vectorization at scale.
**Action:** Always measure custom algorithms implemented in raw Python vs native C-backed vectorized functions like `scipy.optimize.milp`. When iteration counts get to O(100,000) inside Python, the function call/loop overhead dominates, making native solvers much faster even with their setup overhead.

## 2025-03-24 - [React Lazy Loading Eager Fetching Issue]
**Learning:** In a tabbed React application, simply mounting all `<Suspense>` wrapped `React.lazy()` components and hiding them via CSS (e.g. `hidden` attribute or Tailwind `hidden` class) defeats the purpose of code splitting. React will still eagerly fetch all the JavaScript chunks for every tab on initial load, because the components are rendered into the DOM (even if visually hidden). This inflates the initial JS bundle size and increases the Time to Interactive.
**Action:** When using `React.lazy()` with CSS-hidden tabs to preserve state, implement a `visitedTabs` mechanism (e.g., a `Set`). Only conditionally render the lazy component once its corresponding tab has been visited for the first time (`{visitedTabs.has('tab_name') && <Component />}`). This defers the network request for the chunk until the user actually needs it, while still allowing the component to remain mounted (and retain local state) when they switch away.

## 2026-03-24 - [Avoid Python list recreation inside tight numpy loops]
**Learning:** In the Column Generation solver's tight iteration loop, converting a SciPy result array to a Python list, and then wrapping that list *back* into a `np.array()` to assign into a pre-allocated matrix causes redundant memory allocation overhead (`new_pattern = np.round(sub_res.x).astype(int).tolist()` followed by `np.array(new_pattern)`).
**Action:** When working with SciPy optimization results (`res.x`) that need to be inserted into pre-allocated NumPy constraint matrices, operate directly on the NumPy arrays (`np.rint(res.x).astype(int)`) and only convert to `tuple` or `list` for set lookups or JSON serialization if required, avoiding the intermediate redundant `np.array(list)` conversions.
