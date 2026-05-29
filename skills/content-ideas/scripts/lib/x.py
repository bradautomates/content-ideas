"""X / Twitter fetchers. Text-only: no comment or transcript endpoints."""

from . import dates
from .http import sc_get
from .urls import extract_handle_from_url


def fetch_profile(handle, api_key):
    """GET /v1/twitter/user-tweets — recent tweets for a handle."""
    data = sc_get("/v1/twitter/user-tweets", {"handle": handle, "trim": "true"}, api_key)
    if not data:
        return []
    posts = []
    for tweet in (data.get("tweets") or []):
        legacy = tweet.get("legacy") or {}
        views = tweet.get("views") or {}
        posts.append({
            "text": legacy.get("full_text", ""),
            "url": tweet.get("url", ""),
            "author": handle,
            "date": dates.parse_x_date(legacy.get("created_at")),
            "platform": "x",
            "engagement": {
                "likes": legacy.get("favorite_count", 0),
                "reposts": legacy.get("retweet_count", 0),
                "replies": legacy.get("reply_count", 0),
                "bookmarks": legacy.get("bookmark_count", 0),
                "views": int(views.get("count", 0)) if views.get("count") else 0,
            },
        })
    return posts


def fetch_post(url, api_key):
    """GET /v1/twitter/tweet — a single tweet by URL."""
    data = sc_get("/v1/twitter/tweet", {"url": url}, api_key)
    if not data:
        return None
    legacy = data.get("legacy") or data
    views = data.get("views") or {}
    return {
        "text": legacy.get("full_text", "") or data.get("text", ""),
        "url": url,
        "author": extract_handle_from_url(url, "x") or "",
        "date": dates.parse_x_date(legacy.get("created_at")),
        "platform": "x",
        "engagement": {
            "likes": legacy.get("favorite_count", 0),
            "reposts": legacy.get("retweet_count", 0),
            "replies": legacy.get("reply_count", 0),
            "bookmarks": legacy.get("bookmark_count", 0),
            "views": int(views.get("count", 0)) if views.get("count") else 0,
        },
    }
