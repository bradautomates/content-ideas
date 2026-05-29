"""TikTok fetchers: profile videos, single video, comments, transcript."""

import re

from . import dates
from .http import sc_get
from .urls import extract_handle_from_url

MAX_COMMENTS = 10


def _engagement(stats):
    return {
        "views": stats.get("play_count", 0),
        "likes": stats.get("digg_count", 0),
        "comments": stats.get("comment_count", 0),
        "shares": stats.get("share_count", 0),
        "saves": stats.get("collect_count", 0),
    }


def fetch_profile(handle, api_key):
    """GET /v3/tiktok/profile/videos — recent videos for a handle."""
    data = sc_get("/v3/tiktok/profile/videos", {"handle": handle, "sort_by": "latest"}, api_key)
    if not data:
        return []
    posts = []
    for item in (data.get("aweme_list") or []):
        author_name = (item.get("author") or {}).get("unique_id", handle)
        aweme_id = item.get("aweme_id", "")
        posts.append({
            "text": item.get("desc", ""),
            "url": f"https://www.tiktok.com/@{author_name}/video/{aweme_id}" if aweme_id else "",
            "author": author_name,
            "date": dates.timestamp_to_date(item.get("create_time")),
            "platform": "tiktok",
            "engagement": _engagement(item.get("statistics") or {}),
        })
    return posts


def fetch_post(url, api_key):
    """GET /v1/tiktok/video — a single video by URL."""
    data = sc_get("/v1/tiktok/video", {"url": url}, api_key)
    if not data:
        return None
    author_info = data.get("author") or {}
    return {
        "text": data.get("desc", ""),
        "url": url,
        "author": author_info.get("unique_id", "") or extract_handle_from_url(url, "tiktok") or "",
        "date": dates.timestamp_to_date(data.get("create_time")),
        "platform": "tiktok",
        "engagement": _engagement(data.get("statistics") or {}),
    }


def fetch_comments(post_url, api_key):
    """GET /v1/tiktok/video/comments — top comments for a video."""
    data = sc_get("/v1/tiktok/video/comments", {"url": post_url}, api_key)
    if not data:
        return []
    comments = []
    for c in (data.get("comments") or [])[:MAX_COMMENTS]:
        user = c.get("user") or {}
        comments.append({
            "author": user.get("nickname", ""),
            "text": c.get("text", ""),
            "likes": c.get("digg_count", 0),
        })
    return comments


def fetch_transcript(post_url, api_key):
    """GET /v1/tiktok/video/transcript — WebVTT cleaned to plain text."""
    data = sc_get("/v1/tiktok/video/transcript", {"url": post_url}, api_key)
    if not data:
        return None
    transcript = data.get("transcript", "")
    if not transcript:
        return None
    cleaned = []
    for line in transcript.split("\n"):
        line = line.strip()
        if not line or line.startswith("WEBVTT") or "-->" in line or re.match(r"^\d{2}:\d{2}", line):
            continue
        cleaned.append(line)
    return " ".join(cleaned) if cleaned else None
