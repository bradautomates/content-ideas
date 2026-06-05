"""Reddit fetchers: subreddit posts, single post, comments, transcript.

Tracking model is **subreddit-centric**, not user-centric: ScrapeCreators
exposes posts-in-a-subreddit, not posts-by-a-reddit-user. So the `handle`
passed in is a subreddit name (with or without the `r/` prefix), and the
`author` field on each returned post is the post submitter — useful as
display metadata but not the grouping key.
"""

from . import dates
from .http import sc_get

MAX_COMMENTS = 10


def _normalize_subreddit(handle):
    """Accept `r/ClaudeAI`, `/r/ClaudeAI`, or bare `ClaudeAI`. Return bare name."""
    return handle.strip().lstrip("/").removeprefix("r/")


def _engagement(item):
    return {
        "ups": item.get("ups", 0),
        "downs": item.get("downs", 0),
        "comments": item.get("num_comments", 0),
        "score": item.get("score", 0),
        "upvote_ratio": item.get("upvote_ratio", 0),
    }


def _permalink(item, fallback_sub):
    """Build canonical reddit permalink from post id + subreddit."""
    post_id = item.get("id", "")
    sr = item.get("subreddit") or fallback_sub
    if post_id and sr:
        return f"https://www.reddit.com/r/{sr}/comments/{post_id}/"
    return item.get("url") or ""


def fetch_profile(handle, api_key):
    """GET /v1/reddit/subreddit — recent posts in a subreddit."""
    subreddit = _normalize_subreddit(handle)
    data = sc_get("/v1/reddit/subreddit", {"subreddit": subreddit, "trim": "true"}, api_key)
    if not data:
        return []
    posts = []
    for item in (data.get("posts") or []):
        title = item.get("title", "") or ""
        selftext = item.get("selftext", "") or ""
        text = title + (("\n\n" + selftext) if selftext else "")
        posts.append({
            "text": text,
            "url": _permalink(item, subreddit),
            "author": item.get("author", "") or "",
            "date": dates.timestamp_to_date(item.get("created_utc") or item.get("created")),
            "platform": "reddit",
            "engagement": _engagement(item),
            "subreddit": item.get("subreddit") or subreddit,
        })
    return posts


def fetch_post(url, api_key):
    """GET /v1/reddit/post/comments — single post by URL (post body comes back with the comments)."""
    data = sc_get("/v1/reddit/post/comments", {"url": url}, api_key)
    if not data:
        return None
    post = data.get("post") or {}
    if not post:
        return None
    title = post.get("title", "") or ""
    selftext = post.get("selftext", "") or ""
    text = title + (("\n\n" + selftext) if selftext else "")
    sr = post.get("subreddit", "")
    return {
        "text": text,
        "url": url,
        "author": post.get("author", "") or "",
        "date": dates.timestamp_to_date(post.get("created_utc") or post.get("created")),
        "platform": "reddit",
        "engagement": _engagement(post),
        "subreddit": sr,
    }


def fetch_comments(post_url, api_key):
    """GET /v1/reddit/post/comments — top comments for a post."""
    data = sc_get("/v1/reddit/post/comments", {"url": post_url}, api_key)
    if not data:
        return []
    comments = []
    for c in (data.get("comments") or [])[:MAX_COMMENTS]:
        comments.append({
            "author": c.get("author", "") or "",
            "text": c.get("body", "") or "",
            "likes": c.get("score", 0) or c.get("ups", 0) or 0,
        })
    return comments


def fetch_transcript(post_url, api_key):
    """GET /v1/reddit/post/transcript — transcript for video posts (rare)."""
    data = sc_get("/v1/reddit/post/transcript", {"url": post_url}, api_key)
    if not data:
        return None
    transcripts = data.get("transcripts") or data.get("transcript")
    if isinstance(transcripts, str):
        return transcripts or None
    if isinstance(transcripts, list):
        texts = [t.get("text", "") for t in transcripts if isinstance(t, dict) and t.get("text")]
        return " ".join(texts) if texts else None
    return None
