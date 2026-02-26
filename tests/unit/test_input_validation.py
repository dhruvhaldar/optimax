import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add root to path
sys.path.append(os.getcwd())

from api.index import app
import api.limiter

class TestInputValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Clear rate limiter to avoid 429 during tests
        api.limiter.rate_limit_store.clear()

    def test_stochastic_scenario_name_valid(self):
        """Test that a valid alphanumeric scenario name is accepted."""
        payload = {
            "total_land": 500,
            "scenarios": [
                {
                    "name": "Scenario_1",
                    "probability": 1.0,
                    "yields": [2.5, 3.0, 20.0]
                }
            ]
        }
        response = self.client.post("/api/stochastic", json=payload)
        self.assertEqual(response.status_code, 200)

    def test_stochastic_scenario_name_too_long(self):
        """Test that a scenario name exceeding the length limit is rejected."""
        long_name = "A" * 51  # Limit will be 50
        payload = {
            "total_land": 500,
            "scenarios": [
                {
                    "name": long_name,
                    "probability": 1.0,
                    "yields": [2.5, 3.0, 20.0]
                }
            ]
        }
        response = self.client.post("/api/stochastic", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_stochastic_scenario_name_invalid_chars(self):
        """Test that a scenario name with special characters is rejected."""
        invalid_name = "Scenario<script>"
        payload = {
            "total_land": 500,
            "scenarios": [
                {
                    "name": invalid_name,
                    "probability": 1.0,
                    "yields": [2.5, 3.0, 20.0]
                }
            ]
        }
        response = self.client.post("/api/stochastic", json=payload)
        self.assertEqual(response.status_code, 422)

if __name__ == '__main__':
    unittest.main()
