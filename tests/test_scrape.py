"""Tests for the scrape CLI's recency-window logic (--days / --since)."""

import unittest

import helpers  # noqa: F401

import scrape
from lib.dates import days_ago


class WindowDaysTests(unittest.TestCase):
    def test_default_when_absent_or_garbage(self):
        self.assertEqual(scrape.DEFAULT_DAYS, scrape._window_days(""))
        self.assertEqual(scrape.DEFAULT_DAYS, scrape._window_days("abc"))

    def test_clamped_to_bounds(self):
        self.assertEqual(90, scrape.MAX_DAYS)                           # cap is a quarter
        self.assertEqual(scrape.MAX_DAYS, scrape._window_days("365"))   # ceiling
        self.assertEqual(1, scrape._window_days("0"))                   # floor
        self.assertEqual(1, scrape._window_days("-5"))

    def test_explicit_value_passes_through(self):
        self.assertEqual(14, scrape._window_days("14"))   # feed range
        self.assertEqual(90, scrape._window_days("90"))   # profile-build range


class EffectiveSinceTests(unittest.TestCase):
    def test_no_since_uses_window_ceiling(self):
        self.assertEqual(days_ago(7), scrape._effective_since("", 7))

    def test_recent_since_narrows_window(self):
        recent = days_ago(3)
        self.assertEqual(recent, scrape._effective_since(recent, 7))

    def test_stale_since_capped_at_window(self):
        # An old cursor can't widen the window past the ceiling.
        self.assertEqual(days_ago(31), scrape._effective_since("2020-01-01", 31))


if __name__ == "__main__":
    unittest.main()
