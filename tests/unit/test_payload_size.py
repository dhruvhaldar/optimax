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

    def test_malformed_content_length(self):
        # Test bypassing limit with malformed or multiple Content-Length headers
        payload = {"data": "x" * 100}

        # Simulating multiple content-length headers (FastAPI/Starlette joins them with a comma)
        headers = {
            "content-length": "3000000, 3000000"
        }
        response = self.client.post("/api/lp", json=payload, headers=headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid Content-Length header")

    def test_chunked_encoding_bypass(self):
        # Test bypassing chunked check using multiple encodings
        # httpx will refuse to send "transfer-encoding": "chunked" if we don't stream the body,
        # but TestClient allows bypassing some checks. We just send it directly.
        headers = {
            "transfer-encoding": "chunked, gzip"
        }
        # Using GET /api/health to avoid Pydantic validation errors (422) that might obscure the 411
        response = self.client.get("/api/health", headers=headers)

        # It should be blocked by our middleware (411)
        self.assertEqual(response.status_code, 411)
        self.assertEqual(response.json()["detail"], "Chunked encoding not supported")

if __name__ == '__main__':
    unittest.main()
