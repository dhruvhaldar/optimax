## 2025-02-17 - Float Overflow Crash in Scientific Backend
**Vulnerability:** Sending `1e308` (max float) to the LP solver caused a server-side crash (500 Internal Server Error) because `scipy.optimize.linprog` returned `None` for the objective function value, which was unhandled.
**Learning:** Standard Pydantic `float` fields allow infinite and NaN values by default, and have no upper/lower bounds. Scientific computing libraries often fail gracefully or catastrophically with such inputs.
**Prevention:** Defined a reusable `SafeFloat` type using `Annotated[float, Field(allow_inf_nan=False, ge=-1e20, le=1e20)]` to enforce strict numerical limits at the API boundary, preventing DoS/crashes.

## 2026-02-24 - Rate Limiter Memory Leak (DoS)
**Vulnerability:** The in-memory rate limiter allowed unbounded growth of the IP store because cleanup was only triggered *after* the limit was exceeded, and only removed *expired* entries. An attacker could flood the server with unique IPs, causing memory exhaustion (DoS).
**Learning:** Rate limiters must strictly enforce memory caps (e.g., using LRU eviction) rather than relying solely on expiration-based cleanup, especially in environments with limited memory (e.g., serverless).
**Prevention:** Implemented strict `MAX_STORE_SIZE` enforcement with LRU eviction in `api/limiter.py` to guarantee bounded memory usage regardless of traffic patterns.
