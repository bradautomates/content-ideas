import unittest

import helpers  # noqa: F401  (sets sys.path)

from lib.scoring import score_engagement


class ScoringTests(unittest.TestCase):
    def test_x_weighting(self):
        score = score_engagement({
            "platform": "x",
            "engagement": {"likes": 10, "reposts": 2, "replies": 1, "bookmarks": 1},
        })
        # 10 + 2*2 + 3*1 + 4*1 = 21
        self.assertEqual(21, score)

    def test_instagram_weighting(self):
        score = score_engagement({
            "platform": "instagram",
            "engagement": {"likes": 100, "comments": 10, "views": 1000},
        })
        # 100 + 3*10 + 0.1*1000 = 230
        self.assertAlmostEqual(230, score)

    def test_tiktok_weighting(self):
        score = score_engagement({
            "platform": "tiktok",
            "engagement": {"likes": 50, "comments": 5, "shares": 2, "saves": 3, "views": 1000},
        })
        # 50 + 15 + 4 + 6 + 50 = 125
        self.assertAlmostEqual(125, score)

    def test_youtube_weighting(self):
        score = score_engagement({
            "platform": "youtube",
            "engagement": {"views": 1000, "likes": 50, "comments": 5},
        })
        # 100 + 50 + 15 = 165
        self.assertAlmostEqual(165, score)

    def test_unknown_platform_sums_numeric(self):
        score = score_engagement({"platform": "mystery", "engagement": {"a": 3, "b": 4, "c": "x"}})
        self.assertEqual(7, score)

    def test_missing_engagement(self):
        self.assertEqual(0, score_engagement({"platform": "x"}))


if __name__ == "__main__":
    unittest.main()
