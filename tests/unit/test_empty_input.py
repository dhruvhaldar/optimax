import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add root to path
sys.path.append(os.getcwd())

from api.index import app

class TestEmptyInput(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_lp_empty_input(self):
        response = self.client.post(
            "/api/lp",
            json={
                "c": [],
                "A_ub": [],
                "b_ub": [],
                "maximize": True
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_colgen_empty_input(self):
        response = self.client.post(
            "/api/colgen",
            json={
                "roll_length": 10,
                "demands": []
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_lagrangian_empty_input(self):
        response = self.client.post(
            "/api/lagrangian",
            json={
                "costs": [],
                "weights": [],
                "capacities": []
            }
        )
        self.assertEqual(response.status_code, 422)

if __name__ == '__main__':
    unittest.main()
