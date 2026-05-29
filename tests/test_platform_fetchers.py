"""Per-platform profile fetchers, normalized against raw API fixtures.

Each platform module imports `sc_get` from lib.http into its own namespace,
so we patch the reference on the platform module itself.
"""

import unittest
from unittest import mock

from helpers import load_fixture

from lib import instagram, tiktok, x, youtube


class XFetcherTests(unittest.TestCase):
    def test_fetch_profile_normalizes(self):
        with mock.patch.object(x, "sc_get", return_value=load_fixture("x_user_tweets")):
            posts = x.fetch_profile("acme", "key")
        self.assertEqual(1, len(posts))
        p = posts[0]
        self.assertEqual("x", p["platform"])
        self.assertEqual("acme", p["author"])
        self.assertEqual("2026-03-20", p["date"])
        self.assertEqual("https://x.com/acme/status/100", p["url"])
        self.assertEqual(100, p["engagement"]["likes"])
        self.assertEqual(5000, p["engagement"]["views"])

    def test_fetch_profile_empty_on_none(self):
        with mock.patch.object(x, "sc_get", return_value=None):
            self.assertEqual([], x.fetch_profile("acme", "key"))

    def test_fetch_post_normalizes(self):
        # URL-mode single tweet: author comes from the URL (the API omits it),
        # views arrives as a string and must be coerced to int.
        resp = {
            "legacy": {"full_text": "single tweet", "created_at": "Wed Mar 20 12:34:56 +0000 2026",
                       "favorite_count": 42, "retweet_count": 5, "reply_count": 2, "bookmark_count": 1},
            "views": {"count": "9000"},
        }
        with mock.patch.object(x, "sc_get", return_value=resp):
            p = x.fetch_post("https://x.com/acme/status/100", "key")
        self.assertEqual("x", p["platform"])
        self.assertEqual("single tweet", p["text"])
        self.assertEqual("acme", p["author"])
        self.assertEqual("2026-03-20", p["date"])
        self.assertEqual(42, p["engagement"]["likes"])
        self.assertEqual(9000, p["engagement"]["views"])

    def test_fetch_post_none_on_empty(self):
        with mock.patch.object(x, "sc_get", return_value=None):
            self.assertIsNone(x.fetch_post("https://x.com/acme/status/100", "key"))


class InstagramFetcherTests(unittest.TestCase):
    def test_fetch_profile_normalizes(self):
        with mock.patch.object(instagram, "sc_get", return_value=load_fixture("instagram_user_posts")):
            posts = instagram.fetch_profile("acme", "key")
        p = posts[0]
        self.assertEqual("instagram", p["platform"])
        self.assertEqual("2024-03-15", p["date"])
        self.assertIn("/p/ABC123/", p["url"])
        self.assertEqual(250, p["engagement"]["likes"])
        self.assertEqual(9000, p["engagement"]["views"])

    def test_caption_string_form(self):
        with mock.patch.object(instagram, "sc_get", return_value={"items": [{"code": "z", "caption": "plain string"}]}):
            posts = instagram.fetch_profile("acme", "key")
        self.assertEqual("plain string", posts[0]["text"])

    def test_fetch_profile_empty_on_none(self):
        with mock.patch.object(instagram, "sc_get", return_value=None):
            self.assertEqual([], instagram.fetch_profile("acme", "key"))

    def test_fetch_post_normalizes(self):
        resp = {
            "user": {"username": "creator"},
            "caption": {"text": "single reel"},
            "taken_at": 1710460800,
            "like_count": 250,
            "comment_count": 12,
            "play_count": 9000,
        }
        with mock.patch.object(instagram, "sc_get", return_value=resp):
            p = instagram.fetch_post("https://www.instagram.com/p/ABC123/", "key")
        self.assertEqual("instagram", p["platform"])
        self.assertEqual("single reel", p["text"])
        self.assertEqual("creator", p["author"])
        self.assertEqual("2024-03-15", p["date"])
        self.assertEqual(250, p["engagement"]["likes"])

    def test_fetch_post_none_on_empty(self):
        with mock.patch.object(instagram, "sc_get", return_value=None):
            self.assertIsNone(instagram.fetch_post("https://www.instagram.com/p/ABC123/", "key"))

    def test_fetch_comments_normalizes_and_caps(self):
        raw = {"comments": [{"user": {"username": f"u{i}"}, "text": f"c{i}", "comment_like_count": i}
                            for i in range(instagram.MAX_COMMENTS + 5)]}
        with mock.patch.object(instagram, "sc_get", return_value=raw):
            comments = instagram.fetch_comments("https://www.instagram.com/p/ABC123/", "key")
        self.assertEqual(instagram.MAX_COMMENTS, len(comments))
        self.assertEqual("u0", comments[0]["author"])

    def test_fetch_transcript_joins_segments(self):
        resp = {"transcripts": [{"text": "hello"}, {"text": "world"}, {"nope": 1}]}
        with mock.patch.object(instagram, "sc_get", return_value=resp):
            self.assertEqual("hello world", instagram.fetch_transcript("https://www.instagram.com/p/ABC123/", "key"))

    def test_fetch_transcript_none_on_empty(self):
        with mock.patch.object(instagram, "sc_get", return_value={"transcripts": []}):
            self.assertIsNone(instagram.fetch_transcript("https://www.instagram.com/p/ABC123/", "key"))


class TikTokFetcherTests(unittest.TestCase):
    def test_fetch_profile_normalizes(self):
        with mock.patch.object(tiktok, "sc_get", return_value=load_fixture("tiktok_profile_videos")):
            posts = tiktok.fetch_profile("acme", "key")
        p = posts[0]
        self.assertEqual("tiktok", p["platform"])
        self.assertEqual("creator", p["author"])
        self.assertIn("/@creator/video/777", p["url"])
        self.assertEqual(100000, p["engagement"]["views"])

    def test_fetch_profile_empty_on_none(self):
        with mock.patch.object(tiktok, "sc_get", return_value=None):
            self.assertEqual([], tiktok.fetch_profile("acme", "key"))

    def test_fetch_post_normalizes(self):
        resp = {
            "desc": "single video",
            "author": {"unique_id": "creator"},
            "create_time": 1710460800,
            "statistics": {"play_count": 5000, "digg_count": 200, "comment_count": 10,
                           "share_count": 3, "collect_count": 1},
        }
        with mock.patch.object(tiktok, "sc_get", return_value=resp):
            p = tiktok.fetch_post("https://www.tiktok.com/@creator/video/777", "key")
        self.assertEqual("tiktok", p["platform"])
        self.assertEqual("single video", p["text"])
        self.assertEqual("creator", p["author"])
        self.assertEqual(5000, p["engagement"]["views"])
        self.assertEqual(200, p["engagement"]["likes"])

    def test_fetch_post_none_on_empty(self):
        with mock.patch.object(tiktok, "sc_get", return_value=None):
            self.assertIsNone(tiktok.fetch_post("https://www.tiktok.com/@creator/video/777", "key"))

    def test_fetch_comments_normalizes_and_caps(self):
        raw = {"comments": [{"user": {"nickname": f"u{i}"}, "text": f"c{i}", "digg_count": i}
                            for i in range(tiktok.MAX_COMMENTS + 5)]}
        with mock.patch.object(tiktok, "sc_get", return_value=raw):
            comments = tiktok.fetch_comments("https://www.tiktok.com/@creator/video/777", "key")
        self.assertEqual(tiktok.MAX_COMMENTS, len(comments))
        self.assertEqual("u0", comments[0]["author"])

    def test_fetch_transcript_strips_webvtt_markup(self):
        # WebVTT header, timestamp cue lines, and cue ranges must all be dropped,
        # leaving only the spoken text.
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nhello there\n\n00:00:03.000 --> 00:00:05.000\nfrom the video"
        with mock.patch.object(tiktok, "sc_get", return_value={"transcript": vtt}):
            out = tiktok.fetch_transcript("https://www.tiktok.com/@creator/video/777", "key")
        self.assertEqual("hello there from the video", out)

    def test_fetch_transcript_none_on_empty(self):
        with mock.patch.object(tiktok, "sc_get", return_value={"transcript": ""}):
            self.assertIsNone(tiktok.fetch_transcript("https://www.tiktok.com/@creator/video/777", "key"))
        with mock.patch.object(tiktok, "sc_get", return_value=None):
            self.assertIsNone(tiktok.fetch_transcript("https://www.tiktok.com/@creator/video/777", "key"))


class YouTubeFetcherTests(unittest.TestCase):
    def test_fetch_profile_normalizes(self):
        with mock.patch.object(youtube, "sc_get", return_value=load_fixture("youtube_channel_videos")):
            posts = youtube.fetch_profile("acme", "key")
        p = posts[0]
        self.assertEqual("youtube", p["platform"])
        # publishDate is the authoritative upload timestamp and must win over
        # publishedTime (which the API intermittently corrupts to "today").
        self.assertEqual("2026-03-20", p["date"])
        self.assertEqual(12000, p["engagement"]["views"])
        # Engagement comes from the *Int fields; reading likeCount/commentCount
        # silently yields 0 (the views-only bug).
        self.assertEqual(300, p["engagement"]["likes"])
        self.assertEqual(25, p["engagement"]["comments"])
        self.assertEqual(900, p["duration"])

    def test_fetch_post_uses_publish_date_and_int_engagement(self):
        # The single-video endpoint returns publishDate (no publishedTime) and
        # *Int engagement fields. Old code read publishedTime/likeCount and got
        # date=None, likes=0, comments=0.
        resp = {
            "title": "Single video",
            "author": {"name": "Creator"},
            "publishDate": "2026-03-20T06:30:22-07:00",
            "viewCountInt": 5000,
            "likeCountInt": 410,
            "commentCountInt": 33,
            "lengthSeconds": 600,
            "description": "desc",
        }
        with mock.patch.object(youtube, "sc_get", return_value=resp):
            p = youtube.fetch_post("https://www.youtube.com/watch?v=abc", "key")
        self.assertEqual("2026-03-20", p["date"])
        self.assertEqual(5000, p["engagement"]["views"])
        self.assertEqual(410, p["engagement"]["likes"])
        self.assertEqual(33, p["engagement"]["comments"])

    def test_warns_when_all_dates_collapse(self):
        # Canary: if every video shares one date (the known API corruption mode),
        # fetch_profile should emit a warning to stderr.
        vids = [
            {"title": f"v{i}", "url": f"u{i}", "publishDate": "2026-05-29T00:00:00Z",
             "viewCountInt": i, "likeCountInt": 0, "commentCountInt": 0}
            for i in range(youtube.CANARY_MIN_VIDEOS)
        ]
        with mock.patch.object(youtube, "sc_get", return_value={"videos": vids}):
            with mock.patch.object(youtube, "log") as mock_log:
                youtube.fetch_profile("acme", "key")
        self.assertTrue(mock_log.called)
        self.assertIn("share date", mock_log.call_args[0][0])

    def test_no_warning_on_varied_dates(self):
        vids = [
            {"title": f"v{i}", "url": f"u{i}", "publishDate": f"2026-05-2{i}T00:00:00Z",
             "viewCountInt": i, "likeCountInt": 0, "commentCountInt": 0}
            for i in range(youtube.CANARY_MIN_VIDEOS)
        ]
        with mock.patch.object(youtube, "sc_get", return_value={"videos": vids}):
            with mock.patch.object(youtube, "log") as mock_log:
                youtube.fetch_profile("acme", "key")
        self.assertFalse(mock_log.called)

    def test_transcript_prefers_plain_text(self):
        resp = {"transcript_only_text": "hello world from the video", "transcript": [], "language": "English"}
        with mock.patch.object(youtube, "sc_get", return_value=resp):
            self.assertEqual("hello world from the video", youtube.fetch_transcript("https://youtu.be/x", "key"))

    def test_transcript_falls_back_to_segments(self):
        resp = {"transcript": [{"text": "hello"}, {"text": "world"}, {"nope": 1}]}
        with mock.patch.object(youtube, "sc_get", return_value=resp):
            self.assertEqual("hello world", youtube.fetch_transcript("https://youtu.be/x", "key"))

    def test_transcript_word_cap(self):
        resp = {"transcript_only_text": " ".join(["w"] * (youtube.TRANSCRIPT_WORD_CAP + 50))}
        with mock.patch.object(youtube, "sc_get", return_value=resp):
            out = youtube.fetch_transcript("https://youtu.be/x", "key")
        self.assertEqual(youtube.TRANSCRIPT_WORD_CAP, len(out.split()))

    def test_transcript_none_on_empty(self):
        with mock.patch.object(youtube, "sc_get", return_value=None):
            self.assertIsNone(youtube.fetch_transcript("https://youtu.be/x", "key"))
        with mock.patch.object(youtube, "sc_get", return_value={"transcript": []}):
            self.assertIsNone(youtube.fetch_transcript("https://youtu.be/x", "key"))


if __name__ == "__main__":
    unittest.main()
