import unittest

import helpers  # noqa: F401

from lib import urls


class DetectPlatformTests(unittest.TestCase):
    def test_detects_each_platform(self):
        self.assertEqual("x", urls.detect_platform("https://x.com/u/status/1"))
        self.assertEqual("x", urls.detect_platform("https://twitter.com/u/status/1"))
        self.assertEqual("instagram", urls.detect_platform("https://www.instagram.com/u/p/AB/"))
        self.assertEqual("tiktok", urls.detect_platform("https://www.tiktok.com/@u/video/9"))
        self.assertEqual("youtube", urls.detect_platform("https://www.youtube.com/watch?v=x"))
        self.assertEqual("youtube", urls.detect_platform("https://youtu.be/abc"))

    def test_unknown_returns_none(self):
        self.assertIsNone(urls.detect_platform("https://example.com/post/1"))


class ExtractHandleTests(unittest.TestCase):
    def test_x(self):
        self.assertEqual("acme", urls.extract_handle_from_url("https://x.com/acme/status/1", "x"))

    def test_instagram_skips_post_segments(self):
        self.assertEqual("acme", urls.extract_handle_from_url("https://www.instagram.com/acme/p/AB/", "instagram"))
        self.assertIsNone(urls.extract_handle_from_url("https://www.instagram.com/p/AB/", "instagram"))

    def test_tiktok(self):
        self.assertEqual("creator", urls.extract_handle_from_url("https://www.tiktok.com/@creator/video/9", "tiktok"))

    def test_youtube_handle(self):
        self.assertEqual("chan", urls.extract_handle_from_url("https://www.youtube.com/@chan/videos", "youtube"))

    def test_no_handle_returns_none(self):
        self.assertIsNone(urls.extract_handle_from_url("https://www.tiktok.com/video/9", "tiktok"))


if __name__ == "__main__":
    unittest.main()
