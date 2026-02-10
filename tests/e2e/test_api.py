from fastapi.testclient import TestClient
import unittest
import sys
import os

# Add root to path
sys.path.append(os.getcwd())

from api.index import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_lp(self):
        payload = {
            "c": [3, 2],
            "A_ub": [[2, 1], [1, 1], [1, 0]],
            "b_ub": [100, 80, 40],
            "maximize": True
        }
        response = self.client.post("/api/lp", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertAlmostEqual(data['fun'], 180.0)

    def test_ip(self):
        payload = {
            "c": [5, 8],
            "A_ub": [[1, 1], [5, 9]],
            "b_ub": [6, 45],
            "maximize": True
        }
        response = self.client.post("/api/ip", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['fun'], 40.0)

    def test_colgen(self):
        payload = {
            "roll_length": 10,
            "demands": [[3, 5], [5, 2]]
        }
        response = self.client.post("/api/colgen", json=payload)
        self.assertEqual(response.status_code, 200)

    def test_lagrangian(self):
        payload = {
            "costs": [[10, 20], [15, 10]],
            "weights": [[2, 5], [3, 2]],
            "capacities": [5, 5]
        }
        response = self.client.post("/api/lagrangian", json=payload)
        self.assertEqual(response.status_code, 200)

    def test_stochastic(self):
        payload = {
            "total_land": 100,
            "scenarios": [
                {"name": "S1", "probability": 0.5, "yields": [3.0, 3.6, 24.0]},
                {"name": "S2", "probability": 0.5, "yields": [2.5, 3.0, 20.0]}
            ]
        }
        response = self.client.post("/api/stochastic", json=payload)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
