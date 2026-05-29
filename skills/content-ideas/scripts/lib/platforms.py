"""Fetcher registries, assembled from the per-platform modules.

Each registry maps a platform name to the relevant callable. Platforms that
lack a capability (X has no comment/transcript endpoint) are simply absent
from that registry.
"""

from . import instagram, tiktok, x, youtube

# Recent posts for a handle: fetch_profile(handle, api_key) -> [post]
PROFILE_FETCHERS = {
    "instagram": instagram.fetch_profile,
    "x": x.fetch_profile,
    "tiktok": tiktok.fetch_profile,
    "youtube": youtube.fetch_profile,
}

# A single post by URL: fetch_post(url, api_key) -> post | None
POST_FETCHERS = {
    "instagram": instagram.fetch_post,
    "x": x.fetch_post,
    "tiktok": tiktok.fetch_post,
    "youtube": youtube.fetch_post,
}

# Top comments for a post URL: fetch_comments(url, api_key) -> [comment]
COMMENT_FETCHERS = {
    "instagram": instagram.fetch_comments,
    "tiktok": tiktok.fetch_comments,
    "youtube": youtube.fetch_comments,
    # X has no comment endpoint in ScrapeCreators
}

# Spoken transcript for a post URL: fetch_transcript(url, api_key) -> str | None
TRANSCRIPT_FETCHERS = {
    "instagram": instagram.fetch_transcript,
    "tiktok": tiktok.fetch_transcript,
    "youtube": youtube.fetch_transcript,
    # X is text-only, no transcripts
}
