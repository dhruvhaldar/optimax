import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add root to path
sys.path.append(os.getcwd())

from api.index import app

class TestPayloadSizeLimit(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_payload_too_large(self):
        # Create a payload that is slightly larger than 2MB
        payload = {"data": "x" * 2_000_001}
        response = self.client.post("/api/lp", json=payload)

        # It should return 413 Payload Too Large
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["detail"], "Payload Too Large")

    def test_payload_normal_size(self):
        # Create a normal-sized payload
        payload = {
            "c": [1.0, 1.0],
            "A_ub": [[1.0, 1.0]],
            "b_ub": [1.0],
            "maximize": True
        }
        response = self.client.post("/api/lp", json=payload)

        # It shouldn't return 413
        self.assertNotEqual(response.status_code, 413)

if __name__ == '__main__':
    unittest.main()
