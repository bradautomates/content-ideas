"""Orchestration tests with the network fully mocked at the registry level."""

import unittest
from unittest import mock

import helpers  # noqa: F401

from lib import pipeline


class FilterSinceTests(unittest.TestCase):
    def test_drops_older_keeps_undated(self):
        results = {"x": {"acme": [
            {"date": "2026-04-01"},
            {"date": "2026-03-01"},
            {"date": None},
            {},
        ]}}
        pipeline.filter_since(results, "2026-03-15")
        kept = results["x"]["acme"]
        self.assertEqual(3, len(kept))  # 04-01 + undated(None) + missing-date
        self.assertNotIn({"date": "2026-03-01"}, kept)

    def test_no_since_is_noop(self):
        results = {"x": {"acme": [{"date": "2020-01-01"}]}}
        pipeline.filter_since(results, "")
        self.assertEqual(1, len(results["x"]["acme"]))


class ScrapeAllTests(unittest.TestCase):
    def test_parallel_fetch_and_unknown_platform(self):
        fake_profiles = {
            "x": lambda h, k: [{"url": f"https://x.com/{h}/status/1", "platform": "x",
                                "engagement": {"likes": 5}}],
        }
        with mock.patch.object(pipeline, "PROFILE_FETCHERS", fake_profiles), \
             mock.patch.object(pipeline, "COMMENT_FETCHERS", {}), \
             mock.patch.object(pipeline, "TRANSCRIPT_FETCHERS", {}):
            results, errors = pipeline.scrape_all({"x": ["acme"], "bogus": ["x"]}, "key")
        self.assertEqual(1, len(results["x"]["acme"]))
        self.assertTrue(any("Unknown platform: bogus" in e for e in errors))

    def test_account_failure_is_recorded_not_fatal(self):
        # A fetcher that raises for one account must not abort the run: the good
        # account still returns, and the failure lands in errors.
        def flaky(handle, key):
            if handle == "bad":
                raise RuntimeError("boom")
            return [{"url": f"https://x.com/{handle}/status/1", "platform": "x", "engagement": {"likes": 5}}]

        with mock.patch.object(pipeline, "PROFILE_FETCHERS", {"x": flaky}), \
             mock.patch.object(pipeline, "COMMENT_FETCHERS", {}), \
             mock.patch.object(pipeline, "TRANSCRIPT_FETCHERS", {}):
            results, errors = pipeline.scrape_all({"x": ["good", "bad"]}, "key")
        self.assertEqual(1, len(results["x"]["good"]))
        self.assertEqual([], results["x"]["bad"])
        self.assertTrue(any("x/bad" in e and "boom" in e for e in errors))

    def test_transcript_enrichment_attaches_to_top_post(self):
        fake_profiles = {
            "tiktok": lambda h, k: [
                {"url": "u-big", "platform": "tiktok", "engagement": {"views": 1000}},
                {"url": "u-small", "platform": "tiktok", "engagement": {"views": 1}},
            ],
        }
        fake_transcripts = {"tiktok": lambda url, k: "spoken words" if url == "u-big" else None}
        with mock.patch.object(pipeline, "PROFILE_FETCHERS", fake_profiles), \
             mock.patch.object(pipeline, "COMMENT_FETCHERS", {}), \
             mock.patch.object(pipeline, "TRANSCRIPT_FETCHERS", fake_transcripts):
            results, _ = pipeline.scrape_all({"tiktok": ["acme"]}, "key")
        posts = {p["url"]: p for p in results["tiktok"]["acme"]}
        self.assertEqual("spoken words", posts["u-big"]["transcript"])
        self.assertNotIn("transcript", posts["u-small"])

    def test_comment_enrichment_attaches_to_top_post(self):
        fake_profiles = {
            "x": lambda h, k: [
                {"url": "u-big", "platform": "x", "engagement": {"likes": 1000}},
                {"url": "u-small", "platform": "x", "engagement": {"likes": 1}},
            ],
        }
        fake_comments = {"x": lambda url, k: [{"author": "fan", "text": "great", "likes": 3}] if url == "u-big" else []}
        with mock.patch.object(pipeline, "PROFILE_FETCHERS", fake_profiles), \
             mock.patch.object(pipeline, "COMMENT_FETCHERS", fake_comments), \
             mock.patch.object(pipeline, "TRANSCRIPT_FETCHERS", {}):
            results, _ = pipeline.scrape_all({"x": ["acme"]}, "key")
        posts = {p["url"]: p for p in results["x"]["acme"]}
        self.assertIn("comments", posts["u-big"])
        self.assertNotIn("comments", posts["u-small"])


class FetchUrlsTests(unittest.TestCase):
    def test_routes_by_url_and_scores(self):
        fake_posts = {"x": lambda url, k: {"url": url, "platform": "x", "text": "claude code",
                                           "engagement": {"likes": 10}}}
        with mock.patch.object(pipeline, "POST_FETCHERS", fake_posts), \
             mock.patch.object(pipeline, "COMMENT_FETCHERS", {}), \
             mock.patch.object(pipeline, "TRANSCRIPT_FETCHERS", {}):
            results, errors = pipeline.fetch_urls(
                ["https://x.com/a/status/1", "https://example.com/bad"], "key",
                pillar_tokens={"claude", "code"},
            )
        self.assertEqual(1, len(results))
        self.assertEqual(10, results[0]["score"])
        self.assertGreater(results[0]["relevance"], 0.0)
        self.assertIsNone(results[0]["baseline"])
        self.assertTrue(any("Unsupported URL" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
