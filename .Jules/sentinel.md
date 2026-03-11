## 2025-02-17 - Float Overflow Crash in Scientific Backend
**Vulnerability:** Sending `1e308` (max float) to the LP solver caused a server-side crash (500 Internal Server Error) because `scipy.optimize.linprog` returned `None` for the objective function value, which was unhandled.
**Learning:** Standard Pydantic `float` fields allow infinite and NaN values by default, and have no upper/lower bounds. Scientific computing libraries often fail gracefully or catastrophically with such inputs.
**Prevention:** Defined a reusable `SafeFloat` type using `Annotated[float, Field(allow_inf_nan=False, ge=-1e20, le=1e20)]` to enforce strict numerical limits at the API boundary, preventing DoS/crashes.

## 2026-02-24 - Rate Limiter Memory Leak (DoS)
**Vulnerability:** The in-memory rate limiter allowed unbounded growth of the IP store because cleanup was only triggered *after* the limit was exceeded, and only removed *expired* entries. An attacker could flood the server with unique IPs, causing memory exhaustion (DoS).
**Learning:** Rate limiters must strictly enforce memory caps (e.g., using LRU eviction) rather than relying solely on expiration-based cleanup, especially in environments with limited memory (e.g., serverless).
**Prevention:** Implemented strict `MAX_STORE_SIZE` enforcement with LRU eviction in `api/limiter.py` to guarantee bounded memory usage regardless of traffic patterns.

## 2026-02-25 - IP Spoofing in Rate Limiter (X-Forwarded-For)
**Vulnerability:** The rate limiter blindly trusted the *first* IP in the `X-Forwarded-For` header (`split(',')[0]`). Attackers could inject a fake `X-Forwarded-For` header (e.g., `X-Forwarded-For: fake-ip`) which Vercel would append to, resulting in `fake-ip, real-ip`. The application would then rate limit the `fake-ip`, allowing the attacker to bypass limits by rotating the fake IP.
**Learning:** In proxy environments (like Vercel/AWS), the `X-Forwarded-For` header is a comma-separated list where the *client-supplied* values come first, and the *proxy-verified* values are appended. The only trustworthy IP is the one added by the infrastructure you control/trust.
**Prevention:** Modified `api/limiter.py` to use the **last** IP in the `X-Forwarded-For` chain (`split(',')[-1]`) as the client identifier, ensuring reliance on the IP reported by the immediate trusted proxy.

## 2026-02-27 - Missing Security Headers on Frontend CDN (Vercel)
**Vulnerability:** The application enforced strong security headers (CSP, X-Frame-Options, etc.) within the backend `api/index.py` middleware, but completely lacked them on the statically served React frontend hosted via Vercel CDN. This left the primary UI exposed to UI redress attacks (Clickjacking) and XSS risks since `index.html` was served without protections.
**Learning:** In decoupled architectures where the backend and frontend are hosted or routed differently (e.g., Vercel static build vs Serverless functions), security headers applied at the backend framework level do NOT propagate to static assets.
**Prevention:** Configured global security headers at the infrastructure level in `vercel.json` (`"headers"` configuration) to guarantee consistent enforcement across both static frontend assets and API routes.

## 2026-03-01 - Denial of Service via ZeroDivisionError in Column Generation
**Vulnerability:** The Column Generation solver (`api/solvers/colgen.py`) did not validate user input widths against zero or negative values. An attacker could supply a width of `0`, which caused a `ZeroDivisionError` when computing `roll_length // widths[i]`, crashing the endpoint with a 500 error and allowing for Denial of Service.
**Learning:** Mathematical operations on user inputs, especially division, must always have strict bounds checking. Pydantic models with `float` types don't prevent zero natively unless strictly configured with `gt=0`.
**Prevention:** Added explicit validation checks in the solver function to ensure that both `roll_length` and all `demand` widths are strictly positive (>0) before proceeding, immediately raising a `ValueError` which FastAPI cleanly maps to a 400 Bad Request.

## 2026-03-03 - ZeroDivisionError in LP Solver Plotting
**Vulnerability:** The LP solver plotting function `plot_lp` in `api/solvers/lp.py` assumed that if coefficient `a2` was zero, `a1` must be non-zero. An attacker could supply a constraint where both `a1` and `a2` are 0, causing a `ZeroDivisionError` when plotting the constraint boundary (`b/a1`), leading to a 500 Internal Server Error (DoS).
**Learning:** Mathematical plotting or calculations based on user-provided coefficients must always handle cases where all coefficients are zero to prevent division by zero errors.
**Prevention:** Added an explicit `elif a1 != 0:` check before attempting to calculate and plot the vertical constraint line. If both coefficients are zero, the constraint is ignored for plotting purposes.

## 2026-03-05 - Denial of Service via Unhandled TypeError in LP Solver
**Vulnerability:** The Linear Programming solver endpoint (`/api/solvers/lp.py`) was vulnerable to a Denial of Service. When `scipy.optimize.linprog` failed to find a feasible solution or otherwise returned `None` for the objective function value (`res.fun`), the application attempted to negate this `NoneType` (`-res.fun`) when `maximize=True`. This threw an unhandled `TypeError`, bypassing standard error handling and crashing the request with a 500 Internal Server Error.
**Learning:** Even with strict Pydantic bounds (like `SafeFloat`), underlying numerical solvers can fail and return `None` for results like the objective value. Python's dynamic typing allows this to propagate until an operation (like unary negation) causes a catastrophic failure.
**Prevention:** Always explicitly check for `None` before performing mathematical operations on solver results, e.g., using a ternary check like `-res.fun if maximize and res.fun is not None else res.fun` to prevent unhandled `TypeError` exceptions.

## 2026-03-08 - Denial of Service via Unhandled IndexError in Lagrangian Solver
**Vulnerability:** The Lagrangian solver endpoint (`/api/solvers/lagrangian.py`) failed to validate that input matrices `costs`, `weights`, and `capacities` had matching dimensions. An attacker could supply valid 2D array shapes but mismatched sizes, which passed Pydantic `List` typing constraints but caused a mathematical `IndexError` deeper in the solver when it attempted to slice rows/columns or iterate using one array's length over another array's index.
**Learning:** Pydantic `List` boundaries handle maximum depths, but they cannot enforce relational consistency between different fields (e.g. `len(costs) == len(weights)`). Missing cross-field dimensional validation allows requests to trigger internal 500 server crashes.
**Prevention:** Before executing any numerical solver algorithms that process multiple matrices, explicitly check their shapes against each other using `numpy.shape` or `ndim` and raise a `ValueError` with clear messaging if a mismatch is detected, effectively returning a 400 Bad Request error.

## 2026-03-10 - Client-Side Denial of Service via Unhandled Nulls
**Vulnerability:** When solvers (LP, Stochastic) failed to find a feasible solution, the backend correctly returned `null` for the objective values. The frontend components (`LPSolver.jsx`, `StochasticSolver.jsx`) unconditionally called `.toFixed()` on these fields. Rendering this threw a `TypeError: Cannot read properties of null`, triggering a complete crash (White Screen of Death) of the React SPA.
**Learning:** In decoupled applications, safe serialization on the backend (e.g., Python `None` to JSON `null`) does not guarantee safe consumption on the frontend. A single unhandled null property in React rendering can crash the entire UI thread, creating a client-side Denial of Service.
**Prevention:** Added explicit `!== null` checks on solver results before formatting numbers with `.toFixed()`, rendering safe fallback text (e.g., "N/A") to fail securely without breaking the application state.

## 2026-03-10 - Server-Side Log Flooding via Empty Arrays
**Vulnerability:** The `StochasticParams` Pydantic model allowed an empty `scenarios` array (`[]`). This bypassed Pydantic's type checks but caused an `IndexError: too many indices for array` deep within NumPy array construction in `api/solvers/stochastic.py`, crashing the request with a 500 error and flooding server logs.
**Learning:** Pydantic lists without explicit `min_length` constraints accept empty arrays, which are often incompatible with downstream NumPy matrix slicing operations (e.g., `[:, 0]`) that assume data exists. Unhandled exceptions at this layer are a prime vector for Log Flooding DoS.
**Prevention:** Added `Field(min_length=1)` to the `scenarios` definition in `api/index.py` to reject empty arrays at the API boundary, returning a safe 422 Unprocessable Entity instead of an internal server crash.