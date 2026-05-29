"""Per-account analysis: engagement score, relevance, baseline, outlier flag."""

import math

from .relevance import score_relevance
from .scoring import score_engagement

OUTLIER_THRESHOLD = 2.0  # z-score units above the account mean


def analyze_results(results, pillar_tokens):
    """Score, baseline, and flag outliers across all scraped data, in place.

    `results` is the {platform: {handle: [posts]}} structure. Each post gains
    `score`, `relevance`, `baseline` (Nx the account mean), and `outlier`.
    """
    for handles in results.values():
        for posts in handles.values():
            if not posts:
                continue

            scores = []
            for post in posts:
                post["score"] = score_engagement(post)
                post["relevance"] = score_relevance(post, pillar_tokens)
                scores.append(post["score"])

            mean = sum(scores) / len(scores) if scores else 0
            std = math.sqrt(sum((s - mean) ** 2 for s in scores) / len(scores)) if len(scores) > 1 else 0

            for post in posts:
                post["baseline"] = round(post["score"] / mean, 1) if mean > 0 else 0
                post["outlier"] = (post["score"] > mean + OUTLIER_THRESHOLD * std) if std > 0 else False
