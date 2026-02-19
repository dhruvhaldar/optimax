import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add root to path
sys.path.append(os.getcwd())

from api.index import app

class TestSecurityHeaders(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_security_headers_present(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

        headers = response.headers

        # Check X-Content-Type-Options
        self.assertIn("X-Content-Type-Options", headers)
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")

        # Check X-Frame-Options
        self.assertIn("X-Frame-Options", headers)
        self.assertEqual(headers["X-Frame-Options"], "DENY")

        # Check Strict-Transport-Security
        self.assertIn("Strict-Transport-Security", headers)
        self.assertTrue("max-age=31536000" in headers["Strict-Transport-Security"])

        # Check Content-Security-Policy
        self.assertIn("Content-Security-Policy", headers)
        self.assertTrue("default-src 'self'" in headers["Content-Security-Policy"])

        # Check Referrer-Policy
        self.assertIn("Referrer-Policy", headers)
        self.assertEqual(headers["Referrer-Policy"], "strict-origin-when-cross-origin")

        # Check Permissions-Policy
        self.assertIn("Permissions-Policy", headers)
        self.assertEqual(headers["Permissions-Policy"], "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()")

        # Check X-Permitted-Cross-Domain-Policies
        self.assertIn("X-Permitted-Cross-Domain-Policies", headers)
        self.assertEqual(headers["X-Permitted-Cross-Domain-Policies"], "none")

    def test_security_headers_on_error(self):
        # Verify headers are present even on 404
        response = self.client.get("/api/nonexistent")
        self.assertEqual(response.status_code, 404)

        headers = response.headers
        self.assertIn("X-Content-Type-Options", headers)
        self.assertIn("X-Frame-Options", headers)
        self.assertIn("Content-Security-Policy", headers)
        self.assertIn("Permissions-Policy", headers)

if __name__ == '__main__':
    unittest.main()
