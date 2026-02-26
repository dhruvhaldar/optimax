from fastapi import Request, HTTPException
from collections import OrderedDict
import time

# Simple in-memory rate limiter using Fixed Window Counter
# Stores timestamps of requests per IP
# This provides protection against DoS attacks on computationally expensive endpoints
rate_limit_store = OrderedDict()
RATE_LIMIT_DURATION = 60 # seconds
RATE_LIMIT_REQUESTS = 20 # requests per duration per IP
MAX_STORE_SIZE = 1000 # Max number of IPs to track to prevent memory leaks

async def check_rate_limit(request: Request):
    """
    Dependency to enforce rate limiting on sensitive endpoints.
    Limits requests to RATE_LIMIT_REQUESTS per RATE_LIMIT_DURATION per IP.
    """
    client_ip = request.client.host
    # Handle X-Forwarded-For (Vercel/proxies)
    # SECURITY: Use the LAST IP in the list. The first IP can be spoofed by the client
    # sending their own X-Forwarded-For header. The last IP is appended by the
    # immediate proxy (Vercel) and is trustworthy.
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[-1].strip()

    now = time.time()

    # LRU Logic: Move to end if exists (recently used)
    if client_ip in rate_limit_store:
        rate_limit_store.move_to_end(client_ip)

    # Memory Leak Protection: Enforce strict limit via LRU eviction
    # If new key and full, pop oldest (first)
    if client_ip not in rate_limit_store and len(rate_limit_store) >= MAX_STORE_SIZE:
        rate_limit_store.popitem(last=False)

    # Get timestamps, defaulting to empty list if new
    timestamps = rate_limit_store.get(client_ip, [])

    # Filter out old requests outside the window for the current IP
    # We only clean up the CURRENT IP's history, not the whole store (O(1) vs O(N))
    valid_timestamps = [t for t in timestamps if now - t < RATE_LIMIT_DURATION]

    # Check limit
    if len(valid_timestamps) >= RATE_LIMIT_REQUESTS:
        # Update store with filtered timestamps even if blocked, to prevent state loss
        rate_limit_store[client_ip] = valid_timestamps
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

    # Record new request
    valid_timestamps.append(now)
    rate_limit_store[client_ip] = valid_timestamps
