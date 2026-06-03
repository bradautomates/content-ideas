"""content-ideas scraper library.

Split out of the original monolithic scrape.py into small, testable modules:

- http      — retrying GET + ScrapeCreators query helper
- log       — stderr progress (keeps stdout clean for JSON)
- dates     — date parsing/normalization helpers
- x / instagram / tiktok / youtube / reddit / bluesky — per-platform
              fetchers, all via the ScrapeCreators API (profile posts, single
              post by URL, comments, transcript). Reddit is subreddit-centric
              (handle = subreddit name); Bluesky lacks comment + transcript
              endpoints (replyCount is included but reply text is not
              retrievable).
- platforms — builds the fetcher registries from the per-platform modules
- scoring   — per-platform weighted engagement score
- relevance — token-overlap relevance against content pillars
- analyze   — per-account baselines + outlier flags
- urls      — platform detection + handle extraction from a post URL
- env       — API key loading (env var > ~/.config/content/.env)
- pipeline  — orchestration (scrape_all, filter_since, fetch_urls)
"""
