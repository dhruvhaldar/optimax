## 2025-02-17 - Float Overflow Crash in Scientific Backend
**Vulnerability:** Sending `1e308` (max float) to the LP solver caused a server-side crash (500 Internal Server Error) because `scipy.optimize.linprog` returned `None` for the objective function value, which was unhandled.
**Learning:** Standard Pydantic `float` fields allow infinite and NaN values by default, and have no upper/lower bounds. Scientific computing libraries often fail gracefully or catastrophically with such inputs.
**Prevention:** Defined a reusable `SafeFloat` type using `Annotated[float, Field(allow_inf_nan=False, ge=-1e20, le=1e20)]` to enforce strict numerical limits at the API boundary, preventing DoS/crashes.

## 2025-02-18 - Thread-Safety Vulnerability in Matplotlib Plotting
**Vulnerability:** The LP, Lagrangian, and Stochastic solvers used Matplotlib's stateful `pyplot` interface (e.g., `plt.plot()`) for generating graphs. In a multi-threaded web server environment (FastAPI), this creates race conditions where concurrent requests can interfere with each other's plots, leading to data leakage (User A sees User B's graph) or application crashes.
**Learning:** `matplotlib.pyplot` maintains a global state that is not thread-safe. Standard scientific plotting tutorials often teach this pattern, which is dangerous for web applications.
**Prevention:** Refactored all plotting code to use the Object-Oriented interface (`Figure`, `FigureCanvasAgg`), which creates isolated figure instances for each request, ensuring thread safety and preventing data leakage.
