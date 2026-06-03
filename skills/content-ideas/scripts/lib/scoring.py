"""Per-platform weighted engagement scoring."""


def score_engagement(post):
    """Compute a weighted engagement score based on the post's platform."""
    e = post.get("engagement", {})
    platform = post.get("platform", "")

    if platform == "x":
        return (e.get("likes", 0)
                + 2 * e.get("reposts", 0)
                + 3 * e.get("replies", 0)
                + 2 * e.get("quotes", 0)
                + 4 * e.get("bookmarks", 0))

    if platform == "instagram":
        return (e.get("likes", 0)
                + 3 * e.get("comments", 0)
                + 0.1 * e.get("views", 0))

    if platform == "tiktok":
        return (e.get("likes", 0)
                + 3 * e.get("comments", 0)
                + 2 * e.get("shares", 0)
                + 2 * e.get("saves", 0)
                + 0.05 * e.get("views", 0))

    if platform == "youtube":
        return (e.get("views", 0) * 0.1
                + e.get("likes", 0)
                + 3 * e.get("comments", 0))

    if platform == "reddit":
        # Reddit's `score` already nets ups - downs. Comments are high-signal
        # (engagement cost is higher than upvoting). Weight upvote_ratio as a
        # quality multiplier — controversial posts score lower even at high ups.
        score = e.get("score", 0) or e.get("ups", 0)
        ratio = e.get("upvote_ratio", 1.0) or 1.0
        return (score * ratio) + (3 * e.get("comments", 0))

    if platform == "bluesky":
        # Bluesky has no native views metric; weight reposts/quotes (active
        # amplification) higher than likes (passive). Replies count without
        # text but still signal engagement depth.
        return (e.get("likes", 0)
                + 2 * e.get("reposts", 0)
                + 2 * e.get("quotes", 0)
                + 3 * e.get("replies", 0))

    # Fallback: sum all numeric values
    return sum(v for v in e.values() if isinstance(v, (int, float)))
