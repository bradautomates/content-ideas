"""Orchestration: parallel profile scraping, URL-mode fetching, enrichment.

These functions tie the per-platform fetchers, scoring, and analysis together.
Progress goes to stderr via log(); only the caller writes JSON to stdout.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .analyze import analyze_results
from .log import log
from .platforms import (
    COMMENT_FETCHERS,
    POST_FETCHERS,
    PROFILE_FETCHERS,
    TRANSCRIPT_FETCHERS,
)
from .relevance import score_relevance
from .scoring import score_engagement
from .urls import detect_platform

MAX_WORKERS = 5
TOP_N_COMMENTS = 3      # fetch comments for top N posts per account
TOP_N_TRANSCRIPTS = 3   # fetch transcripts for top N video posts per account


def filter_since(results, since):
    """Drop posts dated before `since` (YYYY-MM-DD). Undated posts are kept."""
    if not since:
        return
    for handles in results.values():
        for handle, posts in handles.items():
            handles[handle] = [p for p in posts if not p.get("date") or p["date"] >= since]


def _engagement_sum(post):
    """Cheap engagement heuristic for ranking which posts to enrich."""
    return sum(v for v in post.get("engagement", {}).values() if isinstance(v, (int, float)))


def _index_by_url(results):
    """Map post URL -> post object across the whole results structure."""
    url_to_post = {}
    for handles in results.values():
        for posts in handles.values():
            for post in posts:
                if post.get("url"):
                    url_to_post[post["url"]] = post
    return url_to_post


def _top_posts(posts, n):
    return sorted(posts, key=_engagement_sum, reverse=True)[:n]


def scrape_all(config, api_key, since=None):
    """Scrape all platforms in parallel. Returns (results, errors).

    results: {platform: {handle: [posts]}}
    """
    results = {}
    errors = []

    tasks = []
    for platform, handles in config.items():
        if platform not in PROFILE_FETCHERS:
            errors.append(f"Unknown platform: {platform}")
            continue
        for handle in handles:
            tasks.append((platform, handle))

    log(f"⏳ Fetching posts from {len(tasks)} account(s)...")

    def _fetch(platform, handle):
        log(f"  ⏳ {platform}/{handle}")
        try:
            posts = PROFILE_FETCHERS[platform](handle, api_key)
            log(f"  ✓ {platform}/{handle} — {len(posts)} posts")
            return platform, handle, posts, None
        except Exception as e:  # noqa: BLE001 — per-account failures shouldn't abort the run
            log(f"  ✗ {platform}/{handle} — {e}")
            return platform, handle, [], str(e)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(_fetch, p, h) for p, h in tasks]
        for f in as_completed(futures):
            platform, handle, posts, err = f.result()
            results.setdefault(platform, {})[handle] = posts
            if err:
                errors.append(f"{platform}/{handle}: {err}")

    total_posts = sum(len(posts) for handles in results.values() for posts in handles.values())
    log(f"✓ Posts fetched: {total_posts} total")

    if since:
        filter_since(results, since)
        kept = sum(len(posts) for handles in results.values() for posts in handles.values())
        log(f"✓ Filtered to posts on/after {since}: {kept} of {total_posts}")

    _enrich_comments(results, api_key, errors)
    _enrich_transcripts(results, api_key, errors)

    return results, errors


def _enrich_comments(results, api_key, errors):
    """Fetch comments for the top posts per account and attach them in place."""
    tasks = []
    for platform, handles in results.items():
        fetcher = COMMENT_FETCHERS.get(platform)
        if not fetcher:
            continue
        for handle, posts in handles.items():
            for post in _top_posts(posts, TOP_N_COMMENTS):
                if post.get("url"):
                    tasks.append((platform, handle, post["url"], fetcher))
    if not tasks:
        return

    log(f"⏳ Fetching comments for {len(tasks)} top post(s)...")
    url_to_post = _index_by_url(results)

    def _fetch(platform, handle, url, fetcher):
        try:
            return platform, handle, url, fetcher(url, api_key), None
        except Exception as e:  # noqa: BLE001
            return platform, handle, url, [], str(e)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(_fetch, *t) for t in tasks]
        for f in as_completed(futures):
            platform, handle, url, comments, err = f.result()
            if url in url_to_post and comments:
                url_to_post[url]["comments"] = comments
            if err:
                errors.append(f"comments {platform}/{handle}: {err}")

    count = sum(1 for h in results.values() for ps in h.values() for p in ps if p.get("comments"))
    log(f"✓ Comments fetched for {count} post(s)")


def _enrich_transcripts(results, api_key, errors):
    """Fetch transcripts for the top video posts per account and attach them."""
    tasks = []
    for platform, handles in results.items():
        fetcher = TRANSCRIPT_FETCHERS.get(platform)
        if not fetcher:
            continue
        for handle, posts in handles.items():
            for post in _top_posts(posts, TOP_N_TRANSCRIPTS):
                if post.get("url"):
                    tasks.append((platform, handle, post["url"], fetcher))
    if not tasks:
        return

    log(f"⏳ Fetching transcripts for {len(tasks)} video(s)...")
    url_to_post = _index_by_url(results)

    def _fetch(platform, handle, url, fetcher):
        try:
            return platform, handle, url, fetcher(url, api_key), None
        except Exception as e:  # noqa: BLE001
            return platform, handle, url, None, str(e)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(_fetch, *t) for t in tasks]
        for f in as_completed(futures):
            platform, handle, url, transcript, err = f.result()
            if url in url_to_post and transcript:
                url_to_post[url]["transcript"] = transcript
            if err:
                errors.append(f"transcript {platform}/{handle}: {err}")

    count = sum(1 for h in results.values() for ps in h.values() for p in ps if p.get("transcript"))
    log(f"✓ Transcripts fetched for {count} video(s)")


def fetch_urls(urls, api_key, pillar_tokens=None):
    """Fetch individual posts by URL in parallel. Returns (results, errors).

    results is a flat [post] list (not the nested profile-mode structure).
    """
    pillar_tokens = pillar_tokens or set()
    results = []
    errors = []

    tasks = []
    for url in urls:
        platform = detect_platform(url)
        if not platform:
            errors.append(f"Unsupported URL: {url}")
            continue
        tasks.append((url, platform))

    log(f"Fetching {len(tasks)} post(s)...")

    def _fetch_one(url, platform):
        log(f"  {platform}: {url[:80]}")
        fetcher = POST_FETCHERS.get(platform)
        if not fetcher:
            return url, None, f"No fetcher for {platform}"
        try:
            post = fetcher(url, api_key)
            if not post:
                return url, None, f"No data returned for {url}"
            post["score"] = score_engagement(post)
            post["relevance"] = score_relevance(post, pillar_tokens)
            post["baseline"] = None
            post["outlier"] = None
            return url, post, None
        except Exception as e:  # noqa: BLE001
            return url, None, f"{url}: {e}"

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(_fetch_one, url, plat) for url, plat in tasks]
        for f in as_completed(futures):
            url, post, err = f.result()
            if post:
                results.append(post)
            if err:
                errors.append(err)

    # Enrich each post with comments + transcript (these are individual, not top-N)
    for post in results:
        platform = post["platform"]
        url = post["url"]
        comment_fetcher = COMMENT_FETCHERS.get(platform)
        if comment_fetcher:
            try:
                post["comments"] = comment_fetcher(url, api_key)
            except Exception:  # noqa: BLE001
                pass
        transcript_fetcher = TRANSCRIPT_FETCHERS.get(platform)
        if transcript_fetcher:
            try:
                transcript = transcript_fetcher(url, api_key)
                if transcript:
                    post["transcript"] = transcript
                    post["relevance"] = score_relevance(post, pillar_tokens)
            except Exception:  # noqa: BLE001
                pass

    log(f"Done — {len(results)} post(s) fetched, {len(errors)} error(s)")
    return results, errors


# Re-exported so callers can run scoring/analysis without importing analyze directly.
__all__ = [
    "scrape_all", "fetch_urls", "filter_since", "analyze_results",
]
