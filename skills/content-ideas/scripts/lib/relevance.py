"""Relevance scoring: token overlap of a post against the user's content pillars."""

import re

STOPWORDS = frozenset({
    'the', 'a', 'an', 'to', 'for', 'how', 'is', 'in', 'of', 'on',
    'and', 'with', 'from', 'by', 'at', 'this', 'that', 'it', 'my',
    'your', 'i', 'me', 'we', 'you', 'what', 'are', 'do', 'can',
    'its', 'be', 'or', 'not', 'no', 'so', 'if', 'but', 'about',
    'all', 'just', 'get', 'has', 'have', 'was', 'will',
})


def tokenize(text):
    """Lowercase, strip punctuation, remove stopwords and 1-char tokens."""
    words = re.sub(r'[^\w\s]', ' ', text.lower()).split()
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def parse_pillars(pillars_str):
    """Parse a comma-separated pillar string into a token set."""
    if not pillars_str:
        return set()
    tokens = set()
    for pillar in pillars_str.split(","):
        tokens |= tokenize(pillar.strip())
    return tokens


def score_relevance(post, pillar_tokens):
    """Score how relevant a post is to the content pillars (0.0-1.0).

    Blends coverage (fraction of pillar tokens present) with a precision term
    that penalizes posts padded with unrelated text.
    """
    if not pillar_tokens:
        return 0.5  # No pillars = neutral

    text = post.get("text", "") + " " + post.get("description", "") + " " + post.get("transcript", "")
    post_tokens = tokenize(text)

    if not post_tokens:
        return 0.0

    overlap = pillar_tokens & post_tokens
    if not overlap:
        return 0.0

    coverage = len(overlap) / len(pillar_tokens)
    precision = len(overlap) / min(len(post_tokens), len(pillar_tokens) + 4)

    return round(min(1.0, 0.65 * coverage + 0.35 * precision), 2)
