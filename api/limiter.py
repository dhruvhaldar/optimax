from fastapi import Request, HTTPException
from collections import defaultdict
import time

# Simple in-memory rate limiter using Fixed Window Counter
# Stores timestamps of requests per IP
# This provides protection against DoS attacks on computationally expensive endpoints
rate_limit_store = defaultdict(list)
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
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()

    now = time.time()

    # Memory Leak Protection: Cleanup if store grows too large
    if len(rate_limit_store) >= MAX_STORE_SIZE:
        # Identify IPs with no recent requests (all timestamps expired)
        keys_to_remove = []
        for ip, timestamps in rate_limit_store.items():
            # timestamps are appended, so last is newest.
            # If newest is old, all are old.
            if not timestamps or (now - timestamps[-1] > RATE_LIMIT_DURATION):
                 keys_to_remove.append(ip)

        for ip in keys_to_remove:
            del rate_limit_store[ip]

    # Enforce strict limit by removing LRU (Least Recently Used) if still full
    if len(rate_limit_store) >= MAX_STORE_SIZE:
        # Find the IP with the oldest request (LRU)
        # We look at the last request time for each IP (timestamps[-1])
        # Default to 0 if list is empty (shouldn't happen for active IPs)
        oldest_ip = min(rate_limit_store.keys(), key=lambda k: rate_limit_store[k][-1] if rate_limit_store[k] else 0)
        del rate_limit_store[oldest_ip]

    # Filter out old requests outside the window for the current IP
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip]
        if now - t < RATE_LIMIT_DURATION
    ]

    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

    # Record new request
    rate_limit_store[client_ip].append(now)
