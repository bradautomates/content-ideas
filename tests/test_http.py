"""HTTP retry behavior, with urllib mocked (no real network)."""

import io
import json
import unittest
import urllib.error
from unittest import mock

import helpers  # noqa: F401

from lib import http


def _resp(payload):
    """A context-manager stand-in for urlopen's response object."""
    cm = mock.MagicMock()
    cm.__enter__.return_value.read.return_value = json.dumps(payload).encode()
    return cm


class RequestTests(unittest.TestCase):
    def test_success_returns_json(self):
        with mock.patch("urllib.request.urlopen", return_value=_resp({"ok": 1})):
            self.assertEqual({"ok": 1}, http.request("https://x", {}))

    def test_4xx_gives_up_immediately(self):
        err = urllib.error.HTTPError("https://x", 404, "nf", {}, io.BytesIO(b""))
        with mock.patch("urllib.request.urlopen", side_effect=err) as m:
            self.assertIsNone(http.request("https://x", {}))
        self.assertEqual(1, m.call_count)  # no retries on 404

    def test_429_retries_then_succeeds(self):
        err = urllib.error.HTTPError("https://x", 429, "rate", {}, io.BytesIO(b""))
        with mock.patch("time.sleep"), \
             mock.patch("urllib.request.urlopen", side_effect=[err, _resp({"ok": 2})]) as m:
            self.assertEqual({"ok": 2}, http.request("https://x", {}, retries=3))
        self.assertEqual(2, m.call_count)

    def test_network_error_exhausts_retries(self):
        with mock.patch("time.sleep"), \
             mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("down")) as m:
            self.assertIsNone(http.request("https://x", {}, retries=2))
        self.assertEqual(2, m.call_count)


class ScGetTests(unittest.TestCase):
    def test_builds_url_and_headers(self):
        captured = {}

        def fake_request(url, headers, retries=http.MAX_RETRIES):
            captured["url"] = url
            captured["headers"] = headers
            return {"ok": True}

        with mock.patch.object(http, "request", side_effect=fake_request):
            http.sc_get("/v1/twitter/tweet", {"url": "https://x.com/a/status/1"}, "secret")
        self.assertTrue(captured["url"].startswith(f"{http.SC_BASE}/v1/twitter/tweet?"))
        self.assertIn("url=", captured["url"])
        self.assertEqual("secret", captured["headers"]["x-api-key"])


if __name__ == "__main__":
    unittest.main()
