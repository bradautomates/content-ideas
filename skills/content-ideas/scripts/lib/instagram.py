"""Instagram fetchers: profile posts, single post, comments, transcript."""

from . import dates
from .http import sc_get
from .urls import extract_handle_from_url

MAX_COMMENTS = 10


def _engagement(item):
    return {
        "likes": item.get("like_count", 0),
        "comments": item.get("comment_count", 0),
        "views": item.get("play_count") or item.get("ig_play_count", 0),
    }


def _caption_text(caption):
    if isinstance(caption, dict):
        return caption.get("text", "")
    return str(caption) if caption else ""


def fetch_profile(handle, api_key):
    """GET /v2/instagram/user/posts — recent posts/reels for a handle."""
    data = sc_get("/v2/instagram/user/posts", {"handle": handle, "trim": "true"}, api_key)
    if not data:
        return []
    posts = []
    for item in (data.get("items") or []):
        code = item.get("code", "")
        posts.append({
            "text": _caption_text(item.get("caption")),
            "url": f"https://www.instagram.com/{handle}/p/{code}/" if code else "",
            "author": handle,
            "date": dates.timestamp_to_date(item.get("taken_at")),
            "platform": "instagram",
            "engagement": _engagement(item),
        })
    return posts


def fetch_post(url, api_key):
    """GET /v2/instagram/post — a single post by URL."""
    data = sc_get("/v2/instagram/post", {"url": url}, api_key)
    if not data:
        return None
    handle = (data.get("user") or {}).get("username", "")
    return {
        "text": _caption_text(data.get("caption")),
        "url": url,
        "author": handle or extract_handle_from_url(url, "instagram") or "",
        "date": dates.timestamp_to_date(data.get("taken_at")),
        "platform": "instagram",
        "engagement": _engagement(data),
    }


def fetch_comments(post_url, api_key):
    """GET /v2/instagram/post/comments — top comments for a post."""
    data = sc_get("/v2/instagram/post/comments", {"url": post_url}, api_key)
    if not data:
        return []
    comments = []
    for c in (data.get("comments") or [])[:MAX_COMMENTS]:
        user = c.get("user") or {}
        comments.append({
            "author": user.get("username", ""),
            "text": c.get("text", ""),
            "likes": c.get("comment_like_count", 0),
        })
    return comments


def fetch_transcript(post_url, api_key):
    """GET /v2/instagram/media/transcript — spoken content of a reel."""
    data = sc_get("/v2/instagram/media/transcript", {"url": post_url}, api_key)
    if not data:
        return None
    transcripts = data.get("transcripts") or []
    if transcripts and isinstance(transcripts, list):
        texts = [t.get("text", "") for t in transcripts if isinstance(t, dict) and t.get("text")]
        return " ".join(texts) if texts else None
    return None
