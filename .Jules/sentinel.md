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
