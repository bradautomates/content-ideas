# /content-ideas

![content-ideas hero](hero.png)

**An AI content idea generator that does your morning research for you — it reads what's working across X, Instagram, TikTok, and YouTube, then hands you a daily "For You" feed of content ideas framed against your own brand.**

I built this for my own YouTube channel and used it to grow from 700 to over 10,000 subscribers in three months. It's not just for YouTubers — it's for anyone who has to keep producing content: creators, businesses and marketers, personal brands, founders, agencies, newsletter and podcast writers. If your week starts with "what should I make next?", this skill is for you.

Claude Code (recommended — auto-updates via marketplace):
```
/plugin marketplace add bradautomates/content-ideas
/plugin install content-ideas@content-ideas
```

Codex, Cursor, Copilot, Gemini CLI, or any of 50+ [Agent Skills](https://github.com/vercel-labs/skills) hosts:
```bash
npx skills add bradautomates/content-ideas -g
```
(`-g` installs globally for your user, available across all projects. Drop it to scope per-project.)

More install options (claude.ai web, manual) in the [Install](#install) section below.

One [ScrapeCreators](https://scrapecreators.com) API key covers all four platforms — X, Instagram, TikTok, and YouTube (including transcripts). 100 free calls, no card. Nothing else to install: the runtime is pure Python stdlib.

---

## What's new in this fork

This is a fork of [`bradautomates/content-ideas`](https://github.com/bradautomates/content-ideas) — see the original README above for the core concept and install. This section documents what's added on top.

All additions are opt-in: existing single-project users see no behavior change. The four commits on the open PR ([#1](https://github.com/bradautomates/content-ideas/pull/1)) bundle:

### 1. Two more platforms — Reddit + Bluesky

ScrapeCreators supports both; the plugin only wired four. This fork adds them following the same per-platform-module pattern.

- **Reddit** is **subreddit-centric** (ScrapeCreators doesn't expose `/v1/reddit/user/posts`). The "handle" passed to the profile fetcher is a subreddit name (with or without `r/`). Comments + transcripts work. Engagement scoring weights `score × upvote_ratio + 3×comments` so controversial high-vote posts don't dominate.
- **Bluesky** is **user-centric**, mirrors X/IG/YT. No comments endpoint exists yet (replyCount is captured but reply text isn't retrievable). No transcript endpoint (Bluesky is text-only). Engagement weights reposts + quotes 2× and replies 3× (active amplification > passive likes).

Example tracked-accounts files:
```markdown
# Reddit — Tracked Subreddits
| Subreddit | Notes |
| r/ClaudeAI | AI dev community |
| r/Solopreneur | Audience target |

# Bluesky — Tracked Accounts
| Handle | Notes |
| pfrazee.com | AT-proto core |
```

### 2. Credits surfacing (`credits_remaining`)

ScrapeCreators returns `credits_remaining` in nearly every response. Upstream throws it away. This fork captures it at the HTTP layer (`lib/http.py` exposes `get_last_credits_remaining()`), prints `[credits] N` to stderr at end of every run, and writes a single-int sidecar at `$CONTENT_HOME/.last-credits` when `CONTENT_HOME` is set.

External wrappers can read the sidecar to maintain a usage log without making a separate balance probe. Zero extra API calls.

### 3. Multi-project mode (slug-aware, opt-in)

Run multiple non-overlapping content lines from one install — a SaaS site + a personal brand + a side project — each with its own brand profile, tracked accounts, research history, and (recommended) its own ScrapeCreators API key for per-project attribution against a shared credit pool.

```
/content-ideas <slug>       # routes to that project
/content-ideas              # uses ~/.config/content/last-project
```

Per-project state lives at `<CI_ROOT>/projects/<slug>/{brand,research}/`; per-project key at `~/.config/content/<slug>.env`. A first invocation against an unknown slug auto-triggers new-project setup (API key + profile Q&A + tracked accounts).

Multi-project is opt-in via a wrapper script. The skill detects the wrapper at conventional locations (`$CONTENT_IDEAS_HOME/bin/scrape.sh`, the vault convention, or `$CONTENT_HOME/bin/scrape.sh`) and uses it when present. With no wrapper + no slug, single-project mode is unchanged.

A reference wrapper is in the user's vault layer, not the plugin — that's where per-user logging concerns (api-usage.md format, low-credit thresholds, run-log shape) belong. The plugin itself stays vault-agnostic.

### 4. Defensive fix — `relevance.py` None concat

`post.get("description", "")` returns the default only when the key is missing; some platform responses contain explicit `None` for that field and crash the run mid-pipeline. One-line `(post.get(k) or "")` fix.

---

## The problem it solves

The hard part about content is everything *before* the idea: opening four apps, scrolling until something sparks, watching a pile of other people's videos, and trying to hold the patterns in your head just to figure out what's worth making this week. That research grind eats hours.

`/content-ideas` takes over that one job: **idea aggregation.** It sorts through what everyone else in your niche is doing, surfaces what's actually working, and hands you a short list of ideas so you can skip the scroll and go straight to deciding what to make.

It deliberately stops there. It doesn't write your scripts, it doesn't replace your creative judgment, and the ideas it gives you are exactly that — *starting points*. The best version of any idea still has to be yours: your angle, your spin, your format. Think of it as the researcher and editor handing you a briefing, not the creator. It collapses the hours of aggregation; what you build from the brief is still you.

```
/content-ideas
/content-ideas ai video tools
```

## Why this exists

I run a [YouTube channel](https://www.youtube.com/@bradbonanno) and a business, [Solaris Automation](https://www.solarisautomation.io/), so I live downstream of the same question every day: *what should I make next?* I usually start by looking at what's working right now but doing that by hand means doomscrolling and taking notes to spot the patterns.

So I built a skill to do the morning research for me, and used it on my own channel to go **from 700 to over 10,000 subscribers in three months.** It pulls what the creators I watch actually posted, ranks it by engagement instead of recency, reads the comments to see what audiences are actually asking for, and hands me the overperformers plus a few concrete starting-point ideas framed against my own pillars and voice. It's the difference between *browsing* for inspiration and *being briefed* on it.

The personalization is the point. Before it recommends anything, it studies your own content to learn your niche, pillars, and voice. It then checks every idea against what you've already published so it doesn't suggest reruns. Upvote and downvote anything in the feed and it remembers using auto memory: a self-improving loop where every run sharpens the next.

## What people actually use it for

**The daily brief.** `/content-ideas` first thing in the morning. One page: every tracked creator's last week of posts merged with discovered niche outliers, sorted by what's overperforming, plus up to 10 starting-point ideas.

**Niche-scoped ideation.** `/content-ideas ai video tools` biases the feed and the ideas toward a topic. Useful when you're planning a series, a campaign, or chasing a specific trend rather than scanning your whole world.

**Reading the comments at scale.** The skill pulls the comments off competitors' posts and reads them, so you see what audiences are confused about, asking for, or arguing over.

**Competitor teardown on demand.** Drop in a handful of post URLs and get them fetched, scored, and analyzed — hook, format, comments, why it landed — without adding the account to your tracked list. Good for "how did *this* specific post blow up?"

**Profiling your own presence.** During setup it studies your own channels over the last 90 days to characterize your niche, pillars, and voice, so every idea afterward is framed as *you*, not a generic trend report.

## What makes it different

- **It knows your brand.** It watches your own videos and reads your posts first, learning your niche, pillars, and voice and every idea is framed as *you*, not a generic trend report.
- **It reads the comments, not just the metrics.** It pulls all the comments off competitors' posts and analyzes them for the questions, requests, and arguments that point straight at your next angle.
- **It gets smarter every run.** Upvote and downvote anything in the feed; reactions feed a self-improving loop that sharpens what it surfaces over time.
- **It's honest about its lane.** It replaces the research-and-aggregation grind and gives you starting points, not finished scripts. The creative call stays yours.
- **Four platforms today, more coming.** Reads X, Instagram, TikTok, and YouTube through one API key, with more platforms coming soon.

## How it works

1. **You run `/content-ideas`** (optionally with a topic filter). First run walks you through setup; after that it goes straight to the feed.
2. **The scraper pulls recent posts** A recency window (`--days`, default 7, capped at 90) keeps stale posts out.
3. **Everything gets scored by engagement,** normalized across platforms, with overperformers flagged against each creator's baseline and niche outliers surfaced even from accounts you don't track.
4. **Ideas are generated** against your brand profile and checked against your own content history so you don't get told to make something you already made.
5. **A single self-contained HTML page is rendered** with two tabs (Posts + Ideas), embedded data, sort/filter controls, and a reaction layer.
6. **You react** (▲ more like this / ▼ less / a note). Reactions are saved as the substrate for future personalization so the feed learns your taste over time.

### Platform notes

- **X / Twitter is top-tweets, not recent.** The ScrapeCreators X endpoint has no "latest" sort — it returns an account's most *popular* tweets, which the recency window then filters down. So for X you only ever see recent tweets that are *also* high-engagement; an ordinary recent tweet won't appear. The other three platforms (Instagram, TikTok, YouTube) are fetched newest-first, so their feeds reflect everything posted in the window. Practically, expect X to be sparser and skewed toward an account's hits.
- **X has no comments or transcripts.** There are no comment or transcript endpoints for X, so X posts are text-only — the comment-reading and transcript analysis only apply to Instagram, TikTok, and YouTube.

## The feed

A self-contained HTML page with two tabs:

| Tab | What it shows |
|-----|---------------|
| **Posts** | One feed merging every tracked-account post and every discovered niche outlier. Sort by Popular or Recent; filter by creator, platform, and outliers; overperformers carry an intensity-scaled badge so winners are easy to spot. |
| **Ideas** | Up to 10 actionable, differentiated briefs — angle, hook, funnel + CTA, repurposing — backed by competitor performance and your own content history. |

React to any item and the reaction is saved to `$CONTENT_HOME/research/{date}/feedback.json`, feeding future personalization.

## Install

| Surface | Install |
|---------|---------|
| **Claude Code** | `/plugin marketplace add bradautomates/content-ideas` then `/plugin install content-ideas@content-ideas` |
| **Codex, Cursor, Copilot, Gemini CLI, +50 more** | `npx skills add bradautomates/content-ideas -g` |
| **claude.ai** (web) | [Download `content-ideas.skill`](https://github.com/bradautomates/content-ideas/releases/latest) → Settings → Capabilities → Skills → `+` |
| **Manual / dev** | `git clone https://github.com/bradautomates/content-ideas.git ~/.claude/skills/content-ideas` |

### Claude Code

```
/plugin marketplace add bradautomates/content-ideas
/plugin install content-ideas@content-ideas
```

Update later with `/plugin update content-ideas@content-ideas`.

### claude.ai (web)

1. [Download `content-ideas.skill`](https://github.com/bradautomates/content-ideas/releases/latest) from the latest release.
2. Go to Settings → Capabilities → Skills.
3. Click `+` and drop the file in.

Enable "Code execution and file creation" under Capabilities first — the skill shells out to Python, so it won't run without it.

### Codex, Cursor, Copilot, Gemini CLI, and 50+ other hosts

The [Agent Skills](https://github.com/vercel-labs/skills) CLI installs the skill into whatever agents it detects:

```bash
npx skills add bradautomates/content-ideas -g
```

`-g` installs globally for your user (`~/.codex/skills`, `~/.cursor/skills`, etc.); drop it to install into the current project instead. Useful flags:

- `-a, --agent <names…>` — target specific hosts, e.g. `-a codex -a cursor`
- `-l, --list` — list the skills in this repo without installing
- `--copy` — copy files instead of symlinking (for filesystems without symlink support)

The CLI discovers the skill from `SKILL.md` and honors `.codex-plugin/plugin.json` (`"skills": "./skills/"`) and `AGENTS.md`; `SKILL.md` resolves its own scripts from the host cache or the clone.

## First run

The first `/content-ideas` walks you through setup — no separate install step:

1. **API key.** Grab a free [ScrapeCreators](https://scrapecreators.com) key (100 calls, no card) and the skill stores it in `~/.config/content/.env` (one key covers all four platforms).
2. **Your profile.** Share your own handles and the skill scrapes them over a full quarter to characterize your niche, pillars, and voice — the basis for every idea afterward.
3. **Tracked competitors.** Add the creators you want to watch, per platform.

After that, `/content-ideas` goes straight to the feed. A SessionStart hook prints a one-line nudge only when a key is missing — silent once you're set up.

## Usage

```
/content-ideas                       # your full daily feed
/content-ideas ai video tools        # bias the feed + ideas toward a topic
```

Driving the scraper directly (from a checkout):

**Profile mode** — recent posts for tracked accounts:
```bash
python3 skills/content-ideas/scripts/scrape.py '{"x": ["h1"], "instagram": ["h2"]}' \
  --pillars "..." --since 2026-04-15 --days 7
```
`--days N` keeps the last N days (default 7, hard-capped at 90); `--since` can only narrow that window further. The small default keeps the daily feed tight; the wide end is for the one-off profile-building scrape during setup.

**URL mode** — fetch individual posts for ad-hoc analysis:
```bash
python3 skills/content-ideas/scripts/scrape.py urls \
  "https://x.com/u/status/1" "https://instagram.com/p/abc" --pillars "..."
```

Both modes require a ScrapeCreators key. With none configured the scraper stops and shows setup instructions — there is no silent fallback to web search.

## Where your data lives

Everything persists under **`$CONTENT_HOME`** (the `CONTENT_HOME` env var, or `~/Documents/Content` by default) — one stable home, independent of where you invoke the skill:

```
$CONTENT_HOME/   (default ~/Documents/Content)
├── brand/                              Context (built during first-run setup)
│   ├── profile.md                      Niche, audience, platforms, pillars, search terms, goal
│   ├── my-content.md                   Own content performance + audience requests
│   └── tracked-accounts/{platform}.md  Tracked creators per platform
└── research/{YYYY-MM-DD}/              Output, one dated folder per run
    ├── feed-data.json                  Feed data (skill-generated)
    ├── for-you.html                    Rendered feed (generate_feed.py --static)
    └── feedback.json                   Your reactions (when you react in the feed)
```

Credentials live separately in `~/.config/content/.env`. See [FILE-SCHEMAS.md](FILE-SCHEMAS.md) for the exact structure of every file.

## Structure

```
.
├── skills/content-ideas/
│   ├── SKILL.md                        Skill contract — loaded by all surfaces
│   ├── references/content-strategy.md  Angle/hook/funnel/CTA/brief domain knowledge
│   ├── assets/for-you-template.html    For You page template (data embedded by the generator)
│   └── scripts/
│       ├── scrape.py                   Scraper entrypoint (profile / urls / setup)
│       ├── generate_feed.py            Embeds feed data into the template; serves or writes static HTML
│       └── lib/                        Small, unit-tested modules (http, platforms, scoring, relevance, ...)
├── commands/content-ideas.md              Claude Code slash command
├── hooks/                              SessionStart setup-status hook
├── .claude-plugin/                     plugin.json + marketplace.json (Claude Code)
├── .codex-plugin/                      plugin.json (Codex)
├── AGENTS.md → CLAUDE.md               Codex / generic-agent entry point
├── scripts/build-skill.sh              Builds dist/content-ideas.skill for claude.ai upload
├── tests/                              Unit tests (python3 -m unittest discover -s tests)
└── .github/workflows/                  validate.yml (tests) + release.yml (auto-builds the .skill on tag)
```

## Develop

```bash
# Run the test suite (stdlib only — no pip install needed):
python3 -m unittest discover -s tests -p "test_*.py"

# Build the claude.ai upload bundle:
bash scripts/build-skill.sh      # → dist/content-ideas.skill
```

Releasing: tag `vX.Y.Z`, push the tag. The workflow builds `dist/content-ideas.skill` and attaches it to the GitHub release. Keep the version in sync across `pyproject.toml`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, and `SKILL.md` — `tests/test_plugin_contract.py` enforces it.

## Open source

MIT license. Runtime is dependency-free Python stdlib; scraping via the [ScrapeCreators](https://scrapecreators.com) API.

Built by Brad Bonanno — I make content about building with AI on [YouTube (@bradbonanno)](https://www.youtube.com/@bradbonanno), and build AI operating systems for businesses at [Solaris Automation](https://www.solarisautomation.io/). If this skill saves you a morning scroll, come say hi on the channel.

---

[github.com/bradautomates/content-ideas](https://github.com/bradautomates/content-ideas) · [@bradbonanno](https://www.youtube.com/@bradbonanno) · [Solaris Automation](https://www.solarisautomation.io/) · [LICENSE](LICENSE)
