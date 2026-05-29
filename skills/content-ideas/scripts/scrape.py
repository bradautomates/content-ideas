#!/usr/bin/env python3
"""content-ideas scraper CLI — thin entrypoint over lib/.

Fetches recent posts for tracked accounts, scores engagement and relevance,
flags outliers, and enriches top posts with comments/transcripts.

Usage:
    python3 scrape.py '{"instagram": ["h1"], "x": ["h2"]}' --pillars "AI agents, claude code" --since 2026-04-15
    python3 scrape.py urls "https://x.com/u/status/1" "https://instagram.com/p/abc" --pillars "..."

Both modes require SCRAPECREATORS_API_KEY (env var or ~/.config/content/.env).

Profile mode always enforces a recency window so a run never surfaces stale
posts (the API often returns months of history):
  --days N      keep only posts from the last N days (default 7, capped at 90).
  --since DATE  YYYY-MM-DD; drops posts before that day (the incremental cursor).
The effective cutoff is whichever is *more recent* — so --since narrows the
window but --days is a hard ceiling it can never exceed. Undated posts are kept.
URL mode ignores both (you asked for those specific posts by hand).

Output: JSON on stdout. Progress on stderr.
    profile mode -> {"results": {platform: {handle: [posts]}}, "errors": [...]}
    urls mode    -> {"results": [post, ...], "errors": [...]}
"""

import json
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from lib import pipeline  # noqa: E402
from lib.analyze import analyze_results  # noqa: E402
from lib.dates import days_ago  # noqa: E402
from lib.env import load_api_key  # noqa: E402
from lib.log import log  # noqa: E402
from lib.relevance import parse_pillars  # noqa: E402

# Recency window for profile mode. DEFAULT_DAYS is the daily-feed target (a week);
# MAX_DAYS is a hard backstop against unbounded history. The feed stays tight via
# its small default, while one-off profile builds pass a larger --days (up to 90).
DEFAULT_DAYS = 7
MAX_DAYS = 90

USAGE = (
    "Usage: python3 scrape.py '{json}' --pillars '...' [--since YYYY-MM-DD] [--days N]\n"
    "       python3 scrape.py urls <url> [url...] --pillars '...'\n"
)

NO_KEY_ERROR = {"error": "No SCRAPECREATORS_API_KEY found. Add it to ~/.config/content/.env."}


def _parse_flag(argv, flag):
    """Return the value following `flag` in argv, or '' if absent."""
    for i, arg in enumerate(argv):
        if arg == flag and i + 1 < len(argv):
            return argv[i + 1]
    return ""


def _window_days(raw):
    """Resolve the --days value to an int in [1, MAX_DAYS] (default DEFAULT_DAYS)."""
    try:
        n = int(raw)
    except (ValueError, TypeError):
        return DEFAULT_DAYS
    return max(1, min(n, MAX_DAYS))


def _effective_since(since, days):
    """Combine the incremental cursor with the recency ceiling.

    Returns whichever cutoff date is *more recent*, so --since can narrow the
    window but never widen it past `days` ago.
    """
    cutoff = days_ago(days)
    return max(since, cutoff) if since else cutoff


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    if len(argv) < 2:
        sys.stderr.write(USAGE)
        return 1

    pillars_str = _parse_flag(argv, "--pillars")
    since = _parse_flag(argv, "--since")
    days = _window_days(_parse_flag(argv, "--days"))
    pillar_tokens = parse_pillars(pillars_str)
    api_key = load_api_key()

    # Every platform (including YouTube transcripts) goes through ScrapeCreators
    # now, so both modes need the key.
    if not api_key:
        print(json.dumps(NO_KEY_ERROR))
        return 1

    if argv[1] == "urls":
        flag_values = {pillars_str, since, _parse_flag(argv, "--days")}
        urls = [a for a in argv[2:] if not a.startswith("--") and a not in flag_values]
        if not urls:
            sys.stderr.write(USAGE)
            return 1
        start = time.time()
        results, errors = pipeline.fetch_urls(urls, api_key, pillar_tokens)
        log(f"✓ Done ({time.time() - start:.1f}s) — {len(results)} post(s)")
        json.dump({"results": results, "errors": errors}, sys.stdout, indent=2)
        return 0

    try:
        config = json.loads(argv[1])
    except json.JSONDecodeError:
        print(json.dumps({"error": f"First argument must be a JSON object of {{platform: [handles]}}. Got: {argv[1]!r}"}))
        return 1
    cutoff = _effective_since(since, days)
    log(f"Recency window: posts on/after {cutoff} (last {days}d cap; --since {since or 'none'})")
    start = time.time()
    results, errors = pipeline.scrape_all(config, api_key, since=cutoff)

    log("Scoring and analyzing...")
    analyze_results(results, pillar_tokens)

    total = sum(len(posts) for handles in results.values() for posts in handles.values())
    log(f"Done ({time.time() - start:.1f}s) -- {total} posts across {len(results)} platform(s)")

    json.dump({"results": results, "errors": errors}, sys.stdout, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
