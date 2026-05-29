"""Platform detection and handle extraction from post URLs (URL mode)."""


def detect_platform(url):
    """Detect platform from a post URL. Returns platform string or None."""
    url_lower = url.lower()
    if "x.com/" in url_lower or "twitter.com/" in url_lower:
        return "x"
    if "instagram.com/" in url_lower:
        return "instagram"
    if "tiktok.com/" in url_lower:
        return "tiktok"
    if "youtube.com/" in url_lower or "youtu.be/" in url_lower:
        return "youtube"
    return None


def extract_handle_from_url(url, platform):
    """Best-effort handle extraction from a post URL. Returns handle or None."""
    try:
        if platform == "x":
            # https://x.com/handle/status/123
            parts = url.split("/")
            idx = next(i for i, p in enumerate(parts) if p in ("x.com", "twitter.com"))
            return parts[idx + 1] if idx + 1 < len(parts) else None
        if platform == "instagram":
            # https://www.instagram.com/handle/p/CODE/ or /reel/CODE/
            parts = url.rstrip("/").split("/")
            idx = next(i for i, p in enumerate(parts) if "instagram.com" in p)
            candidate = parts[idx + 1] if idx + 1 < len(parts) else None
            return candidate if candidate not in ("p", "reel", "reels", "stories", "tv") else None
        if platform == "tiktok":
            # https://www.tiktok.com/@handle/video/123
            for p in url.split("/"):
                if p.startswith("@"):
                    return p.lstrip("@")
            return None
        if platform == "youtube":
            # https://www.youtube.com/@handle/... or /channel/ID
            for p in url.split("/"):
                if p.startswith("@"):
                    return p.lstrip("@")
            return None
    except (StopIteration, IndexError):
        return None
    return None
