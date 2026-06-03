"""Bluesky fetchers: user posts, single post.

User-centric tracking like X/Instagram/YouTube. ScrapeCreators does not
expose a comments endpoint for Bluesky — replies are counted in
`replyCount` but the reply *text* is not retrievable. Likewise no
transcript endpoint (Bluesky is primarily text). Both `fetch_comments`
and `fetch_transcript` exist for API uniformity but are intentionally
absent from the registries in `platforms.py`.
"""

from datetime import datetime

from .http import sc_get


def _normalize_handle(handle):
    """Strip a leading `@` if the user wrote `@pfrazee.com`; pass through otherwise."""
    return handle.strip().lstrip("@")


def _engagement(item):
    return {
        "likes": item.get("likeCount", 0) or 0,
        "reposts": item.get("repostCount", 0) or 0,
        "replies": item.get("replyCount", 0) or 0,
        "quotes": item.get("quoteCount", 0) or 0,
    }


def _post_text(item):
    record = item.get("record") or {}
    return record.get("text", "") or ""


def _post_date(item):
    """Bluesky returns ISO 8601 in `indexedAt` and `record.createdAt`. Prefer createdAt."""
    record = item.get("record") or {}
    raw = record.get("createdAt") or item.get("indexedAt")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _post_url(item, handle):
    """Construct the bsky.app web URL from the AT-proto URI.

    URI shape: at://did:plc:.../app.bsky.feed.post/{rkey}
    Web URL shape: https://bsky.app/profile/{handle}/post/{rkey}
    """
    uri = item.get("uri") or ""
    rkey = uri.rsplit("/", 1)[-1] if "/" in uri else ""
    if rkey and handle:
        return f"https://bsky.app/profile/{handle}/post/{rkey}"
    return ""


def fetch_profile(handle, api_key):
    """GET /v1/bluesky/user/posts — recent posts for a Bluesky handle."""
    norm = _normalize_handle(handle)
    data = sc_get("/v1/bluesky/user/posts", {"handle": norm}, api_key)
    if not data:
        return []
    posts = []
    for item in (data.get("feed") or []):
        author = (item.get("author") or {}).get("handle") or norm
        posts.append({
            "text": _post_text(item),
            "url": _post_url(item, author),
            "author": author,
            "date": _post_date(item),
            "platform": "bluesky",
            "engagement": _engagement(item),
        })
    return posts


def fetch_post(url, api_key):
    """GET /v1/bluesky/post — a single post by URL."""
    data = sc_get("/v1/bluesky/post", {"url": url}, api_key)
    if not data:
        return None
    item = data.get("post") or data
    author = (item.get("author") or {}).get("handle") or ""
    return {
        "text": _post_text(item),
        "url": url,
        "author": author,
        "date": _post_date(item),
        "platform": "bluesky",
        "engagement": _engagement(item),
    }
