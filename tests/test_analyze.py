import unittest

import helpers  # noqa: F401

from lib.analyze import analyze_results


class AnalyzeTests(unittest.TestCase):
    def _x(self, likes):
        return {"platform": "x", "engagement": {"likes": likes}}

    def test_scores_relevance_baseline_outlier_assigned(self):
        results = {"x": {"acme": [self._x(10), self._x(20), self._x(30)]}}
        analyze_results(results, set())
        posts = results["x"]["acme"]
        for p in posts:
            self.assertIn("score", p)
            self.assertIn("relevance", p)
            self.assertIn("baseline", p)
            self.assertIn("outlier", p)

    def test_baseline_relative_to_account_mean(self):
        results = {"x": {"acme": [self._x(10), self._x(20), self._x(30)]}}
        analyze_results(results, set())
        posts = results["x"]["acme"]
        # mean = 20 -> baselines 0.5, 1.0, 1.5
        self.assertEqual(0.5, posts[0]["baseline"])
        self.assertEqual(1.0, posts[1]["baseline"])
        self.assertEqual(1.5, posts[2]["baseline"])

    def test_outlier_flag_on_extreme(self):
        # One huge post among small ones should trip the z-score threshold.
        # Note: a single spike among n identical values has max z-score
        # sqrt(n-1), so n must be >=6 for it to clear the 2.0 cutoff.
        results = {"x": {"acme": [self._x(1)] * 5 + [self._x(100)]}}
        analyze_results(results, set())
        posts = results["x"]["acme"]
        self.assertTrue(posts[-1]["outlier"])
        self.assertFalse(posts[0]["outlier"])

    def test_empty_account_skipped(self):
        results = {"x": {"acme": []}}
        analyze_results(results, set())  # must not raise
        self.assertEqual([], results["x"]["acme"])


if __name__ == "__main__":
    unittest.main()
