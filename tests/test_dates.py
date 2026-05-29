import unittest

from helpers import load_fixture  # noqa: F401  (ensures sys.path is set)

from lib import dates


class DatesTests(unittest.TestCase):
    def test_timestamp_to_date(self):
        self.assertEqual("2024-03-15", dates.timestamp_to_date(1710460800))
        self.assertEqual("2024-03-15", dates.timestamp_to_date("1710460800"))

    def test_timestamp_to_date_invalid(self):
        self.assertIsNone(dates.timestamp_to_date(None))
        self.assertIsNone(dates.timestamp_to_date(""))
        self.assertIsNone(dates.timestamp_to_date("bad"))

    def test_parse_x_date(self):
        self.assertEqual("2026-03-20", dates.parse_x_date("Wed Mar 20 12:34:56 +0000 2026"))

    def test_parse_x_date_invalid(self):
        self.assertIsNone(dates.parse_x_date(None))
        self.assertIsNone(dates.parse_x_date(""))
        self.assertIsNone(dates.parse_x_date("not-a-date"))


if __name__ == "__main__":
    unittest.main()
