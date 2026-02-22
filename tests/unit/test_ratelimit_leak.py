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

            # 2. Advance time past duration so all previous entries are expired
            # We add slight buffer to ensure strictly greater
            new_time = start_time + RATE_LIMIT_DURATION + 1.0

            with patch('time.time', return_value=new_time):
                # Add one more request (MAX_STORE_SIZE + 1)
                # Cleanup condition is if len > MAX_STORE_SIZE.
                # Current len is MAX_STORE_SIZE. So this call won't trigger cleanup BEFORE processing.
                # But it will add the new IP.
                ip_new1 = "10.0.0.1"
                req1 = MagicMock()
                req1.client.host = ip_new1
                req1.headers = {}
                await check_rate_limit(req1)

                # Store size should now be MAX_STORE_SIZE + 1
                self.assertEqual(len(rate_limit_store), MAX_STORE_SIZE + 1)

                # Add another request. Now len is MAX_STORE_SIZE + 1, which is > MAX_STORE_SIZE.
                # This should trigger cleanup.
                ip_new2 = "10.0.0.2"
                req2 = MagicMock()
                req2.client.host = ip_new2
                req2.headers = {}
                await check_rate_limit(req2)

                # Cleanup should have removed the initial MAX_STORE_SIZE entries because they are expired.
                # The remaining entries should be ip_new1 and ip_new2.
                self.assertLess(len(rate_limit_store), MAX_STORE_SIZE)
                self.assertEqual(len(rate_limit_store), 2)
                self.assertIn(ip_new1, rate_limit_store)
                self.assertIn(ip_new2, rate_limit_store)

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
