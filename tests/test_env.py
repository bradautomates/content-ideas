import os
import unittest
from unittest import mock

import helpers  # noqa: F401

from lib import env


class LoadApiKeyTests(unittest.TestCase):
    def test_env_var_takes_precedence(self):
        with mock.patch.dict(os.environ, {"SCRAPECREATORS_API_KEY": "from-env"}):
            self.assertEqual("from-env", env.load_api_key(env_path="/nonexistent"))

    def test_reads_from_env_file(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with helpers.tmp_env_file("SCRAPECREATORS_API_KEY=from-file\nSETUP_COMPLETE=true\n") as p:
                self.assertEqual("from-file", env.load_api_key(env_path=p))

    def test_strips_quotes(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with helpers.tmp_env_file('SCRAPECREATORS_API_KEY="quoted-key"\n') as p:
                self.assertEqual("quoted-key", env.load_api_key(env_path=p))

    def test_missing_returns_empty(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual("", env.load_api_key(env_path="/nonexistent/.env"))


if __name__ == "__main__":
    unittest.main()
