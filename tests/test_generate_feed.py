import json
import unittest
from pathlib import Path

import helpers  # noqa: F401

import generate_feed

FIXTURE_FEED = {
    "meta": {"date": "March 20, 2026", "subtitle": "s", "footer": "f"},
    "posts": [
        {
            "title": "A post",
            "text": "summary",
            "url": "https://x.com/acme/1",
            "handle": "@acme",
            "displayName": "Acme Co",
            "platform": "x",
            "timestamp": "2026-03-20T09:00:00Z",
            "sortValue": 3200,
            "engagement": {"likes": 300, "views": 3200},
            "zScore": 3.1,
            "comments": [],
        }
    ],
    "ideas": {"items": [{"title": "Idea", "concept": "c", "funnel": "mofu"}]},
}


class LoadTests(unittest.TestCase):
    def test_load_feed_and_feedback(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            run = Path(d)
            (run / "feed-data.json").write_text(json.dumps(FIXTURE_FEED))
            (run / "feedback.json").write_text(json.dumps({
                "reviews": [{"item_id": "ideas::Idea", "rating": "up", "note": "yes"}],
            }))
            feed = generate_feed.load_feed(run / "feed-data.json")
            self.assertEqual("March 20, 2026", feed["meta"]["date"])
            state = generate_feed.load_feedback_state(run / "feedback.json")
            self.assertEqual("up", state["ideas::Idea"]["rating"])

    def test_load_feed_missing(self):
        self.assertIsNone(generate_feed.load_feed(Path("/nope/feed-data.json")))


class GenerateHtmlTests(unittest.TestCase):
    def test_placeholder_replaced_and_data_embedded(self):
        html = generate_feed.generate_html(FIXTURE_FEED, {}, "server")
        self.assertNotIn(generate_feed.PLACEHOLDER, html)
        self.assertIn("const FEED_DATA =", html)
        self.assertIn('const FEEDBACK_MODE = "server"', html)
        self.assertIn("March 20, 2026", html)

    def test_template_actually_has_placeholder(self):
        template = generate_feed.DEFAULT_TEMPLATE.read_text()
        self.assertIn(generate_feed.PLACEHOLDER, template)

    def test_static_mode_flag_distinguished(self):
        html = generate_feed.generate_html(FIXTURE_FEED, {}, "static")
        self.assertIn('const FEEDBACK_MODE = "static"', html)


if __name__ == "__main__":
    unittest.main()
