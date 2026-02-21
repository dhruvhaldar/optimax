import sys
import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

# Add root to path
sys.path.append(os.getcwd())

from api.index import app
import api.limiter

class TestRateLimit(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Reset limiter store before each test
        api.limiter.rate_limit_store.clear()

    def test_rate_limit_enforcement(self):
        # The limit is 20 requests per minute
        # We need a bounded problem to ensure solver succeeds
        payload = {
            "c": [1, 1],
            "A_ub": [[1, 0], [0, 1]],
            "b_ub": [1, 1],
            "maximize": True
        }

        # Make 20 requests
        for i in range(20):
            response = self.client.post("/api/lp", json=payload)
            self.assertEqual(response.status_code, 200, f"Request {i+1} failed with {response.text}")

        # The 21st request should fail
        response = self.client.post("/api/lp", json=payload)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json()["detail"], "Rate limit exceeded. Please try again later.")

    def test_health_endpoint_no_limit(self):
        # Verify that health endpoint is not limited
        for i in range(25):
            response = self.client.get("/api/health")
            self.assertEqual(response.status_code, 200)

    @patch('api.limiter.time.time')
    def test_rate_limit_expiry(self, mock_time):
        mock_time.return_value = 1000.0
        payload = {
            "c": [1, 1],
            "A_ub": [[1, 0], [0, 1]],
            "b_ub": [1, 1],
            "maximize": True
        }

        # Exhaust limit
        for _ in range(20):
            self.client.post("/api/lp", json=payload)

        # Verify blocked
        response = self.client.post("/api/lp", json=payload)
        self.assertEqual(response.status_code, 429)

        # Advance time by 61 seconds
        mock_time.return_value = 1061.0

        # Should be allowed again
        response = self.client.post("/api/lp", json=payload)
        self.assertEqual(response.status_code, 200)
