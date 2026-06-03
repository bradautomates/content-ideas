---
description: Build today's For You feed — scrape tracked competitors across X, Instagram, TikTok, YouTube (+ Reddit, Bluesky in this fork), score what's performing, and turn it into actionable content ideas.
argument-hint: "[<project-slug>] — multi-project mode only; omit for last-used project (bare /content-ideas works too)"
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

Invoke the `content-ideas` skill (defined in `skills/content-ideas/SKILL.md`) with the user's arguments: $ARGUMENTS

Follow the skill's full pipeline: resolve project (multi-project mode if a slug
is given or `~/.config/content/last-project` exists) → first-run / new-project
setup check → resolve `$CONTENT_HOME` → scrape tracked competitors (and the
user's own channels for the brand profile) → score and rerank by real engagement
→ generate the self-contained For You HTML feed → surface the top posts and
content ideas. If this is a first run / new project and no API key is configured
for that scope, walk the user through setup before scraping.
