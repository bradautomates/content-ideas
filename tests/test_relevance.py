import unittest

import helpers  # noqa: F401

from lib import relevance


class RelevanceTests(unittest.TestCase):
    def test_tokenize_drops_stopwords_and_short(self):
        toks = relevance.tokenize("How to build AI agents with Claude")
        self.assertNotIn("to", toks)
        self.assertNotIn("how", toks)
        self.assertIn("build", toks)
        self.assertIn("agents", toks)
        self.assertIn("claude", toks)

    def test_parse_pillars(self):
        toks = relevance.parse_pillars("AI agents, claude code")
        self.assertEqual({"ai", "agents", "claude", "code"}, toks)

    def test_no_pillars_is_neutral(self):
        self.assertEqual(0.5, relevance.score_relevance({"text": "anything"}, set()))

    def test_no_overlap_is_zero(self):
        toks = relevance.parse_pillars("quantum biology")
        self.assertEqual(0.0, relevance.score_relevance({"text": "claude code agents"}, toks))

    def test_empty_text_is_zero(self):
        toks = relevance.parse_pillars("claude code")
        self.assertEqual(0.0, relevance.score_relevance({"text": ""}, toks))

    def test_strong_match_scores_high(self):
        toks = relevance.parse_pillars("claude code agents")
        score = relevance.score_relevance({"text": "building claude code agents today"}, toks)
        self.assertGreater(score, 0.6)
        self.assertLessEqual(score, 1.0)

    def test_uses_description_and_transcript(self):
        toks = relevance.parse_pillars("claude code")
        post = {"text": "", "description": "claude", "transcript": "code"}
        self.assertGreater(relevance.score_relevance(post, toks), 0.0)


if __name__ == "__main__":
    unittest.main()
