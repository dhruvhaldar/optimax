import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add root to path
sys.path.append(os.getcwd())

from api.index import app
import api.limiter

class TestColGenDoS(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        api.limiter.rate_limit_store.clear()

    def test_colgen_large_roll_length(self):
        """Test that a massive roll_length does not crash the server with OOM."""
        payload = {
            "roll_length": 1e9,
            "demands": [[3, 5], [5, 2]]
        }
        response = self.client.post("/api/colgen", json=payload)
        # Should be rejected with 400 or 422 before causing OOM
        self.assertIn(response.status_code, [400, 422])

if __name__ == '__main__':
    unittest.main()
