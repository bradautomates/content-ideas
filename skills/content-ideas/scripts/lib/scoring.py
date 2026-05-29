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

    # Fallback: sum all numeric values
    return sum(v for v in e.values() if isinstance(v, (int, float)))
