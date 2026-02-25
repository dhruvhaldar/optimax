import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add root to path
sys.path.append(os.getcwd())

from api.index import app
import api.limiter

class TestRateLimitBypass(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Reset limiter store before each test
        api.limiter.rate_limit_store.clear()

    def test_ip_spoofing_prevention(self):
        """
        Simulates an attacker trying to bypass rate limiting by spoofing X-Forwarded-For headers.
        The attacker sends: 'spoofed-ip, real-ip'.
        If the app uses the first IP (spoofed), rate limiting is bypassed.
        If the app uses the last IP (real), rate limiting is enforced.
        """
        payload = {
            "c": [1, 1],
            "A_ub": [[1, 0], [0, 1]],
            "b_ub": [1, 1],
            "maximize": True
        }

        real_ip = "203.0.113.1"
        limit = api.limiter.RATE_LIMIT_REQUESTS # 20

        # Make 'limit' requests, each with a DIFFERENT spoofed IP but SAME real IP
        for i in range(limit):
            spoofed_ip = f"10.0.0.{i}"
            headers = {"X-Forwarded-For": f"{spoofed_ip}, {real_ip}"}
            response = self.client.post("/api/lp", json=payload, headers=headers)
            self.assertEqual(response.status_code, 200, f"Request {i+1} failed unexpectedly")

        # The (limit + 1)th request should be BLOCKED because it comes from the same real IP
        spoofed_ip = f"10.0.0.{limit}"
        headers = {"X-Forwarded-For": f"{spoofed_ip}, {real_ip}"}
        response = self.client.post("/api/lp", json=payload, headers=headers)

        # This assertion will FAIL if the vulnerability exists (status code will be 200)
        self.assertEqual(response.status_code, 429, "Rate limit bypassed via IP spoofing!")

if __name__ == '__main__':
    unittest.main()
