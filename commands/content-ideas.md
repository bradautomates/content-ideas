---
description: Build today's For You feed — scrape tracked competitors across X, Instagram, TikTok, and YouTube, score what's performing, and turn it into actionable content ideas.
argument-hint: "[topic filter] — e.g. \"ai video tools\" (optional; omit for your full feed)"
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

Invoke the `content-ideas` skill (defined in `skills/content-ideas/SKILL.md`) with the user's arguments: $ARGUMENTS

Follow the skill's full pipeline: first-run setup check → resolve `$CONTENT_HOME` →
scrape tracked competitors (and the user's own channels for the brand profile) →
score and rerank by real engagement → generate the self-contained For You HTML feed →
surface the top posts and content ideas. If a topic filter was provided, bias the
feed toward it. If this is a first run and no API key is configured, walk the user
through setup before scraping.
