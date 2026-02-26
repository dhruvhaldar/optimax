import unittest
from collections import defaultdict
import time
from unittest.mock import MagicMock, patch
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.limiter import check_rate_limit, rate_limit_store, RATE_LIMIT_DURATION, MAX_STORE_SIZE

class TestRateLimiterMemoryLeak(unittest.TestCase):
    def setUp(self):
        # Clear the store before each test
        rate_limit_store.clear()

    def test_cleanup_mechanism(self):
        async def run_test():
            # 1. Fill store up to MAX_STORE_SIZE
            start_time = 1000.0

            with patch('time.time', return_value=start_time):
                for i in range(MAX_STORE_SIZE):
                    ip = f"192.168.1.{i}"
                    request = MagicMock()
                    request.client.host = ip
                    request.headers = {}
                    await check_rate_limit(request)

            # Verify store is full
            self.assertEqual(len(rate_limit_store), MAX_STORE_SIZE)

            # Verify the first item inserted is at the beginning (LRU)
            first_ip = list(rate_limit_store.keys())[0]
            self.assertEqual(first_ip, "192.168.1.0")

            # 2. Advance time past duration
            new_time = start_time + RATE_LIMIT_DURATION + 1.0

            with patch('time.time', return_value=new_time):
                # Add one more request (MAX_STORE_SIZE + 1)
                # With LRU, this should evict the oldest item ("192.168.1.0")
                # and keep size at MAX_STORE_SIZE
                ip_new1 = "10.0.0.1"
                req1 = MagicMock()
                req1.client.host = ip_new1
                req1.headers = {}
                await check_rate_limit(req1)

                # Store size should remain at MAX_STORE_SIZE (stable memory usage)
                self.assertEqual(len(rate_limit_store), MAX_STORE_SIZE)

                # The new IP should be present
                self.assertIn(ip_new1, rate_limit_store)

                # The oldest IP should be gone
                self.assertNotIn("192.168.1.0", rate_limit_store)

                # The second oldest should now be first
                self.assertEqual(list(rate_limit_store.keys())[0], "192.168.1.1")

                # Add another request.
                ip_new2 = "10.0.0.2"
                req2 = MagicMock()
                req2.client.host = ip_new2
                req2.headers = {}
                await check_rate_limit(req2)

                self.assertEqual(len(rate_limit_store), MAX_STORE_SIZE)
                self.assertIn(ip_new2, rate_limit_store)
                self.assertNotIn("192.168.1.1", rate_limit_store)

        asyncio.run(run_test())

    def test_overflow_protection(self):
        """
        Verify that the rate limiter does not grow indefinitely when flooded with unique active IPs.
        """
        async def run_test():
            # 1. Fill the store to MAX_STORE_SIZE with ACTIVE requests
            current_time = 1000.0

            with patch('time.time', return_value=current_time):
                for i in range(MAX_STORE_SIZE + 100):
                    ip = f"10.0.0.{i}"
                    req = MagicMock()
                    req.client.host = ip
                    req.headers = {}
                    await check_rate_limit(req)

            # 2. Check the size of the store
            self.assertEqual(len(rate_limit_store), MAX_STORE_SIZE, "Rate limit store grew beyond maximum size!")

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
