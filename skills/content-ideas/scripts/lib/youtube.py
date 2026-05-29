"""YouTube fetchers: channel videos, single video, comments, transcript.

All via the ScrapeCreators API — no external binaries required.
"""

from .http import sc_get
from .log import log
from .urls import extract_handle_from_url

MAX_COMMENTS = 10
TRANSCRIPT_WORD_CAP = 5000  # bound feed-data size on very long videos
CANARY_MIN_VIDEOS = 5  # only flag a date collapse once there are enough videos to be suspicious


def fetch_profile(handle, api_key):
    """GET /v1/youtube/channel-videos — recent videos for a channel handle."""
    data = sc_get(
        "/v1/youtube/channel-videos",
        {"handle": handle, "sort": "latest", "includeExtras": "true"},
        api_key,
    )
    if not data:
        return []
    posts = []
    for vid in (data.get("videos") or []):
        posts.append({
            "text": vid.get("title", ""),
            "url": vid.get("url", ""),
            "author": handle,
            # Prefer publishDate (true upload timestamp): the channel-videos
            # endpoint intermittently returns publishedTime = today for every
            # video, but publishDate stays correct in those same responses.
            "date": (vid.get("publishDate") or vid.get("publishedTime") or "")[:10] or None,
            "platform": "youtube",
            "engagement": {
                "views": vid.get("viewCountInt", 0),
                "likes": vid.get("likeCountInt", 0),
                "comments": vid.get("commentCountInt", 0),
            },
            "duration": vid.get("lengthSeconds"),
            "description": vid.get("description", ""),
        })
    _warn_on_date_collapse(handle, posts)
    return posts


def _warn_on_date_collapse(handle, posts):
    """Canary: warn when every dated video shares one identical date.

    The channel-videos endpoint intermittently corrupts dates (returns the same
    value for every video). Preferring publishDate avoids the known case, but if
    both date fields ever collapse, this surfaces it loudly rather than letting a
    feed silently fill with stale-but-same-dated posts.
    """
    dated = [p["date"] for p in posts if p.get("date")]
    if len(dated) >= CANARY_MIN_VIDEOS and len(set(dated)) == 1:
        log(f"  ⚠ {handle}: all {len(dated)} videos share date {dated[0]} — likely a bad API response; dates may be unreliable.")


def fetch_post(url, api_key):
    """GET /v1/youtube/video — a single video by URL."""
    data = sc_get("/v1/youtube/video", {"url": url}, api_key)
    if not data:
        return None
    return {
        "text": data.get("title", ""),
        "url": url,
        "author": (data.get("author") or {}).get("name", "") or extract_handle_from_url(url, "youtube") or "",
        # The single-video endpoint returns publishDate (not publishedTime).
        # Prefer it; fall back to publishedTime for forward-compat.
        "date": (data.get("publishDate") or data.get("publishedTime") or "")[:10] or None,
        "platform": "youtube",
        "engagement": {
            "views": data.get("viewCountInt", 0),
            "likes": data.get("likeCountInt", 0),
            "comments": data.get("commentCountInt", 0),
        },
        "duration": data.get("lengthSeconds"),
        "description": data.get("description", ""),
    }


def fetch_comments(post_url, api_key):
    """GET /v1/youtube/video/comments — top comments for a video."""
    data = sc_get("/v1/youtube/video/comments", {"url": post_url, "order": "top"}, api_key)
    if not data:
        return []
    comments = []
    for c in (data.get("comments") or [])[:MAX_COMMENTS]:
        author = c.get("author") or {}
        engagement = c.get("engagement") or {}
        comments.append({
            "author": author.get("name", ""),
            "text": c.get("content", ""),
            "likes": engagement.get("likes", 0),
        })
    return comments


def fetch_transcript(post_url, api_key):
    """GET /v1/youtube/video/transcript — plain-text transcript (any language).

    Prefers the API's `transcript_only_text`; falls back to joining the
    structured `transcript` segments. Capped at TRANSCRIPT_WORD_CAP words.
    """
    data = sc_get("/v1/youtube/video/transcript", {"url": post_url}, api_key)
    if not data:
        return None
    text = data.get("transcript_only_text")
    if not text:
        segments = data.get("transcript") or []
        text = " ".join(s.get("text", "") for s in segments if isinstance(s, dict) and s.get("text"))
    text = (text or "").strip()
    if not text:
        return None
    words = text.split()
    return " ".join(words[:TRANSCRIPT_WORD_CAP])
