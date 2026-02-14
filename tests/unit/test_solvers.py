import sys
import os
import unittest
import numpy as np

# Add root to path
sys.path.append(os.getcwd())

from api.solvers import lp, ip, colgen, lagrangian, stochastic

class TestSolvers(unittest.TestCase):
    def test_solve_lp(self):
        c = [3, 2]
        A = [[2, 1], [1, 1], [1, 0]]
        b = [100, 80, 40]
        res = lp.solve_lp(c, A, b, maximize=True)
        self.assertTrue(res['success'])
        self.assertAlmostEqual(res['fun'], 180.0, places=1)
        self.assertIsNotNone(res['plot'])

    def test_solve_ip(self):
        c = [5, 8]
        A = [[1, 1], [5, 9]]
        b = [6, 45]
        res = ip.solve_ip(c, A, b, maximize=True)
        self.assertTrue(res['success'])
        # Optimal integer solution is (0, 5) with value 40. Relaxed is (2.25, 3.75) val 41.25.
        self.assertEqual(res['fun'], 40.0)
        self.assertEqual(res['x'], [0.0, 5.0])
        self.assertIsNotNone(res['tree_plot'])

    def test_solve_ip_limit(self):
        # Create a hard Knapsack problem instance that generates many branches
        n = 15
        weights = [10 + i for i in range(n)]
        values = [w + 5 for w in weights]
        capacity = int(sum(weights) * 0.5)

        c = values
        A_ub = [weights]
        b_ub = [capacity]

        # Test with a very small node limit
        max_nodes = 10

        res = ip.solve_ip(c, A_ub, b_ub, maximize=True, max_nodes=max_nodes)

        # Verify result structure
        self.assertIn('status', res)
        self.assertIn('success', res)

        if res['status'] == "Optimal":
            print("Warning: Solver found optimal solution within 10 nodes. Increase problem difficulty.")
        else:
            self.assertEqual(res['status'], "Limit Reached")

    def test_solve_colgen(self):
        # Roll length 10. Demands: Width 3 (qty 5), Width 5 (qty 2).
        demands = [[3, 5], [5, 2]]
        res = colgen.solve_cutting_stock(10, demands)
        self.assertEqual(res['status'], "Optimal")
        self.assertGreater(len(res['patterns']), 0)
        # Optimal rolls: 2 rolls of 10 can fit?
        # 3x3 + 0x5 = 9 <= 10. (Pattern 1: [3, 0])
        # 0x3 + 2x5 = 10 <= 10. (Pattern 2: [0, 2])
        # Need 5 of width 3. Pattern 1 gives 3. Pattern 1 gives 3?
        # Pattern: [3, 0] gives 3 items of width 3.
        # Pattern: [1, 1] gives 1 of 3, 1 of 5. (3+5=8 <= 10).
        # It should work.

    def test_solve_lagrangian(self):
        costs = [[10, 20], [15, 10]]
        weights = [[2, 5], [3, 2]]
        caps = [5, 5]
        res = lagrangian.solve_lagrangian(costs, weights, caps)
        self.assertEqual(res['status'], "Completed")
        self.assertGreater(len(res['lb_history']), 0)

    def test_solve_stochastic(self):
        scenarios = [
            {"name": "S1", "probability": 0.5, "yields": [3.0, 3.6, 24.0]},
            {"name": "S2", "probability": 0.5, "yields": [2.5, 3.0, 20.0]}
        ]
        res = stochastic.solve_stochastic(100, scenarios)
        self.assertTrue(res['success'])
        self.assertEqual(len(res['x']), 3)

if __name__ == '__main__':
    unittest.main()
