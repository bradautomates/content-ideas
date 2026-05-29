# File Schemas

Structure definitions for the files the content-ideas skill reads and produces.

All persistent files live under **`$CONTENT_HOME`** — the `CONTENT_HOME` env
var, or `~/Documents/Content` by default — never the current working directory.
Credentials are the one exception: they stay in `~/.config/content/.env`.

---

## brand/profile.md

**Created by:** `/content-ideas` first-run setup (or by hand)
**Read by:** `/content-ideas`
**Location:** `$CONTENT_HOME/brand/profile.md` (CONTENT_HOME defaults to `~/Documents/Content`)

No YAML frontmatter. Structured markdown containing brand context and social
profiles:

```markdown
# Content Profile

## Niche
{One-line niche definition}

## Audience
{Who they're creating for}

## Target Platforms
{Ordered by priority — drives which platforms the skill covers}
1. {Platform 1}
2. {Platform 2}
3. {Platform 3}

## Content Pillars
- {Pillar 1}
- {Pillar 2}
- {Pillar 3}

## Search Terms
{Persistent keyword list used by /content-ideas every run. These are always searched
in addition to whatever Claude infers from niche/pillars or the user passes as
an argument. Add, remove, or edit any time.}
- {term 1}
- {term 2}
- {term 3}

## Content Goal
- **Why:** {What they're trying to achieve — lead gen, brand awareness, community building, follower growth, thought leadership, selling a product/service, etc.}
- **Driving to:** {Where traffic/leads go — website URL, booking link, newsletter signup, course/product page, "nowhere yet", etc.}
- **Promoting:** {What they're selling or building toward — consulting services, SaaS product, course, agency, personal brand, nothing specific yet, etc.}

## Voice Notes
{Brief voice/style notes}

## Research Channels
{Platforms to scrape during /content-ideas. Controls which agents launch and how deep
analysis goes. Edit any time — changes take effect on the next /content-ideas run.}

| Platform | Depth | Notes |
|----------|-------|-------|
| {platform} | {standard/subtitles/transcribe/metadata} | {optional — why this platform is here} |

Depth options:
- **standard** — scrape posts + summarize from available text (X, LinkedIn, Reddit)
- **subtitles** — pull subtitles/captions and summarize from transcript (YouTube)
- **transcribe** — pull video transcripts via the scraper (TikTok, Instagram)
- **metadata** — scrape engagement data only, no summaries (lightweight monitoring)

Only platforms listed here get agents during /content-ideas. If a platform is missing,
it won't be scraped regardless of tracked accounts.

## My Social Profiles

### X
- **Handle:** @{handle}
- **Followers:** {count}
- **Bio:** {bio text}
- **Content style:** {brief notes from scraping recent posts}

### Instagram
- **Handle:** @{handle}
- **Followers:** {count}
- **Bio:** {bio text}
- **Content style:** {brief notes}

### TikTok
- **Handle:** @{handle}
- **Followers:** {count}
- **Bio:** {bio text}
- **Content style:** {brief notes}

### YouTube
- **Channel:** {name}
- **Subscribers:** {count}
- **About:** {channel description}
- **Content style:** {brief notes}
```

Only include platform sections for platforms the user is active on.

---

## brand/tracked-accounts/{platform}.md

**Created by:** `/content-ideas` first-run setup (optional — user can skip)
**Read by:** `/content-ideas`
**Location:** `$CONTENT_HOME/brand/tracked-accounts/{platform}.md` (one file per platform)

No YAML frontmatter. Simple list format per platform:

```markdown
# {Platform} — Tracked Accounts

Add accounts you want to track on {Platform} — competitors, inspiration, peers.

| Handle | Category | Notes |
|--------|----------|-------|
| @example | Niche leader | High-quality threads |
```

One file per platform (e.g., `x.md`, `linkedin.md`, `youtube.md`).
Files are created for platforms in Research Channels + platforms the user is active
on. Additional files can be created manually at any time.

---

## Taste profile → auto-memory (no file)

The user's evolving content taste is **no longer a file**. There is no
`brand/learnings.md`. Taste lives in Claude Code's project **auto-memory**
(`~/.claude/projects/<project>/memory/`), which Claude reads and writes on
demand — see SKILL.md Step 1a (record from last run's feedback) and 1b (recall).

- **Source of signals:** the user's reactions to past feeds, captured in
  `research/{date}/feedback.json`, which the next run's Step 1a distills into
  memory.
- **What's stored:** topics/formats/angles the user gravitates toward, creators
  they keep saving, and what doesn't land — the same dimensions the old file
  tracked, but as memory notes Claude maintains (one taste signal per note).
- **Scope:** machine-local and per-repository; not synced. Each user who runs
  the skill builds their own taste memory.
- **Fallback:** if auto-memory is unavailable, the skill uses engagement signals
  (and `brand/my-content.md`) alone; `feedback.json` still persists for later.

---

## brand/my-content.md

**Created by:** `/content-ideas` first-run setup (or by hand)
**Updated by:** `/content-ideas` (each run)
**Read by:** `/content-ideas` (anti-cannibalization, audience requests, performance patterns)
**Location:** `$CONTENT_HOME/brand/my-content.md`

Rolling snapshot of the user's own content performance across all platforms.
Replaced each update (not appended) — sections are fresh analysis, not a log.

```markdown
# My Content Performance

> last_updated: {YYYY-MM-DD}

## Performance Summary

| Platform | Tracked | Avg Engagement | Best Performer | Trend |
|----------|---------|----------------|----------------|-------|
| {platform} | {count} | {avg score} | {title} ({Nx avg}) | {↑ improving / → stable / ↓ declining} |

## What's Working
Patterns with evidence. Replaced each update — current snapshot, not history.
- {pattern} — {evidence: "Videos about X average 2.3x baseline across N posts"}
- {pattern} — {evidence}

## What's Not Working
Patterns with evidence. Same replacement rules.
- {pattern} — {evidence: "Tutorial format at 0.4x baseline across N posts"}
- {pattern} — {evidence}

## Spike Analysis
Posts that hit 3x+ baseline. What triggered each spike and what to replicate.

| Date | Title | Performance | Trigger | Hook | Platform |
|------|-------|-------------|---------|------|----------|
| {YYYY-MM-DD} | {title} | {Nx avg} | {1-sentence trigger explanation} | {mechanism × form} | {platform} |

### Spike Patterns
Synthesized patterns across all spikes. 2-3 evidence-backed bullets.
- {pattern} — {evidence across N spikes}

## Topics Covered
Anti-cannibalization table. All-time — one row per piece of content.
Append new entries, never delete old ones. ~100 bytes/entry.

| Topic | Platform | Date | Title | Performance | URL |
|-------|----------|------|-------|-------------|-----|
| {specific topic label} | {platform} | {YYYY-MM-DD} | {title} | {Nx avg} | {url} |

## Audience Requests
Top 10-15 demand signals aggregated from comments on the user's own content.
Paraphrased request + count + exact quote + engagement. Capped at 15.
Re-ranked and deduplicated each update.

| Request | Count | Best Quote | Quote Engagement | Source |
|---------|-------|------------|------------------|--------|
| {paraphrased request} | {N similar} | "{exact comment}" | {likes/upvotes} | {post URL} |

## Recent Content (Last 30 Days)
Rolling 30-day window per platform. Older content rolls into Topics Covered only.

### {Platform}
| Date | Title | Engagement Score | vs Baseline | URL |
|------|-------|-----------------|-------------|-----|
| {YYYY-MM-DD} | {title} | {score} | {Nx avg} | {url} |
```

**Size management:**
- **Recent Content** — 30-day rolling window. Entries older than 30 days are removed from this section but preserved in Topics Covered.
- **Topics Covered** — grows over time but stays lean (table rows, ~100 bytes/entry). Scales to 500+ pieces.
- **What's Working / What's Not Working** — snapshot analyses, replaced entirely each update. Not cumulative.
- **Spike Analysis** — table rows APPENDED (like Topics Covered). Spike Patterns subsection REPLACED each update with fresh synthesis across all spikes.
- **Audience Requests** — capped at top 15. Deduplicated and re-ranked each update.
- **Performance Summary** — replaced each update. One row per platform.

---

## research/{YYYY-MM-DD}/for-you.html

**Created by:** `generate_feed.py --static` (or served live by `generate_feed.py`)
**Read by:** User (opened in browser)
**Location:** `$CONTENT_HOME/research/{YYYY-MM-DD}/for-you.html`

Self-contained HTML page: all CSS, the client-side renderer, and the feed data
embedded inline. **Never agent-generated by hand.** `generate_feed.py` embeds
`feed-data.json` into `skills/content-ideas/assets/for-you-template.html` (at the
`/*__EMBEDDED_DATA__*/` placeholder) and writes this file. The only external
dependency is Google Fonts.

Two tabbed sections: Posts and Ideas. The Posts tab is one flat, sortable,
filterable feed of every post (tracked-account posts + discovered niche
outliers merged). A sticky control bar offers sort (Popular / Recent),
a creator dropdown, platform chips, and an Outliers toggle; overperforming
posts are flagged with an intensity-scaled badge. Every item carries a
feedback control (▲/▼/note) that writes to `feedback.json`.

In **server mode** the page is regenerated on each load (so re-running the
scraper shows up on refresh) and is not written to disk; use `--static` to
produce this file.

---

## research/{YYYY-MM-DD}/feed-data.json

**Created by:** `/content-ideas` (skill-generated)
**Read by:** `generate_feed.py` (embedded into the page as `const FEED_DATA`)
**Location:** `$CONTENT_HOME/research/{YYYY-MM-DD}/feed-data.json`

A single JSON object — the only feed file the skill writes by hand. The
generator embeds it into the template as `const FEED_DATA = {...}`; all
rendering, CSS, and interactivity live in the template. The structure is shown
below as the embedded JS literal for readability (with field comments); the
JSON file is the same structure with standard double-quoted keys.

```js
const FEED_DATA = {
  meta: {
    date: "March 20, 2026",                    // display date for header + title
    subtitle: "5 platforms scraped · ...",       // header subtitle line
    footer: "March 20, 2026 · Content Research by ..."  // footer text
  },

  posts: [                                     // [] if nothing scraped. ONE flat list —
    {                                          //   tracked-account posts AND discovered
      title: "Post title",                     //   niche outliers, merged. Rendered as the
      text: "Description...",                  //   sortable/filterable Posts tab.
      url: "https://...",                      // source link, opens on click
      handle: "@handle",                       // author handle
      displayName: "Display Name",             // creator label (filter dropdown + card). Falls back to handle
      platform: "x",                           // drives avatar CSS class + platform filter
      timestamp: "2026-03-20T14:30:00Z",       // ISO 8601 — drives "Recent" sort + relative time display
      sortValue: 14965,                        // number — drives "Popular" sort (total engagement or reach)
      time: null,                              // string | null — OPTIONAL display override; else derived from timestamp
      engagement: {                            // engagement bar numbers — populate
        replies: null,                         //   only the metrics the platform
        reposts: 692,                          //   reports; omit/null the rest
        likes: 14965,
        views: null,                           // number | null — reach (IG/TikTok/YT/X)
        bookmarks: 11712                        // number | null — X bookmarks; use
        // saves: 11712                         //   `saves` for IG/TikTok save count
      },
      stats: null,                             // string | null — OPTIONAL pre-formatted fallback if no engagement object
      zScore: 3.56,                            // number | null — niche outlier strength (drives outlier badge + intensity)
      performance: "+68% vs baseline",         // string | null — tracked-account overperformance vs its own baseline
      performanceDirection: "up",              // "up" | "down" | null — "up" also flags the post as an outlier
      why: "Why it's here explanation",        // string | null — insight block text
      hook: "Hook text",                       // string | null — hook callout
      bookmarked: false,                       // true → shows [Bookmarked] badge
      comments: [                              // [] if no notable comments
        {
          handle: "@user",                     // commenter handle
          text: "Comment text",                // comment content
          engagement: "89 likes",              // string | null — engagement display
          signal: "gap identification"         // string | null — signal label
        }
      ]
    }
  ],

  ideas: {
    audienceRequests: [                        // [] if none — banner hidden when empty
      {
        handle: "from your video title",       // source context
        text: "Request text",                  // audience request quote
        engagement: "4 similar · 47 likes",    // string | null
        signal: "angle request"                // string | null
      }
    ],
    items: [                                   // idea cards, up to 10
      {
        title: "Idea title",                   // picks card title
        concept: "Brief concept description",  // picks card body
        funnel: "mofu",                        // "tofu" | "mofu" | "bofu"
        sourceUrl: "https://...",              // primary source link
        pastCoverage: null,                    // string | null — anti-cannibalization callout
        brief: {
          whyNow: "Timing explanation",        // string
          audienceAsking: {                    // null if no audience signals
            text: "Summary text",              // string | null — paragraph after comments
            comments: []                       // same comment shape — embedded quotes
          },
          differentiator: "What makes yours different",  // string
          suggestedHook: "Opening line",       // string — rendered italic/accent
          howToAction: "CTA / next step",      // string
          repurposeAs: ["LinkedIn post", "Instagram reel"]  // string array
        }
      }
    ],
    patterns: [                                // rolling observations, after idea cards
      "**Pattern** observation with evidence." // **bold** → <strong> by renderer
    ]
  }
};
```

**Field types and allowed values:**

| Field | Type | Allowed Values |
|-------|------|---------------|
| `platform` | string | `"x"`, `"reddit"`, `"youtube"`, `"linkedin"`, `"instagram"`, `"tiktok"` |
| `funnel` | string | `"tofu"`, `"mofu"`, `"bofu"` |
| `timestamp` (posts) | string | ISO 8601 (e.g. `"2026-03-20T14:30:00Z"`). Drives the **Recent** sort and the relative-time label (`6h`, `2d`). Missing/unparseable → sorts last, no time shown. |
| `sortValue` (posts) | number | Comparable popularity score (total engagement or reach). Drives the **Popular** sort (default). Missing → sorts last. |
| `performanceDirection` | string \| null | `"up"` (overperforming → flags post as outlier), `"down"` (neutral). |
| `zScore` (posts) | number \| null | Niche-outlier strength. Present → flags post as outlier; magnitude drives badge intensity (z≥2 / ≥3 / ≥4 deepen the accent + add flames). |
| `performance` (posts) | string \| null | Pre-formatted overperformance vs the account's own baseline, e.g. `"+68% vs baseline"`. Shown in the outlier badge when no `zScore`; the leading % drives intensity. |
| `signal` | string \| null | `"angle request"`, `"gap identification"`, `"objection"`, `"experience sharing"`, `"question seeking depth"`, or any descriptive label |
| engagement (comments) | string \| null | Pre-formatted: `"89 likes"`, `"23 upvotes"`, `"4 similar · 47 likes"` |
| engagement (posts) | object \| null | `{ replies, reposts, likes, views, bookmarks \| saves }` — each `number \| null`. Each renders with its own icon (views = eye, bookmarks/saves = bookmark); never put a view count in `bookmarks`. Populate only the metrics the platform reports — null/absent metrics are omitted, not dashed. |
| `stats` (posts) | string \| null | OPTIONAL pre-formatted fallback shown only when `engagement` is absent: `"20K views · 1,300 likes · 107 comments"` |
| `patterns[]` | string | Supports `**bold**` markdown syntax |

**Outlier flag:** a post is treated as an outlier (badge + accent bar) when it
has a `zScore` **or** `performanceDirection: "up"`. Badge intensity (1–4, deeper
color + more flames) scales with `zScore` (≥2/≥3/≥4) or, lacking that, the
percentage parsed from `performance`. Non-outliers render plain.

**Sorting & filtering** happen client-side over the single `posts[]` array; no
ordering is implied by array position. Provide `sortValue` and `timestamp` on
every post so both sorts are meaningful. The creator dropdown is built from
distinct `displayName`/`handle`; platform chips from distinct `platform`.

**Null handling:** `null` values are silently omitted by the renderer.
In the posts engagement bar, a `null`/absent metric is dropped from
the row (so each platform shows only the metrics it reports). Empty arrays `[]`
hide their parent container.

---

## research/{YYYY-MM-DD}/feedback.json

**Created by:** the For You page (browser) — server mode writes it via
`POST /api/feedback`; static mode downloads it for the user to drop in.
**Read by:** `generate_feed.py` (to prepopulate reactions on reload) and the
**next** `/content-ideas` run at Step 1a, which distills durable reactions into
auto-memory taste signals that personalize future runs.
**Location:** `$CONTENT_HOME/research/{YYYY-MM-DD}/feedback.json`

```json
{
  "reviews": [
    {
      "item_id": "ideas::I tried the 30-day morning routine",   // stable id: "<tab>::<post-url or title>"
      "tab": "ideas",                                            // "posts" | "ideas"
      "label": "I tried the 30-day morning routine",            // card title (human-readable)
      "rating": "up",                                    // "up" | "down" | null
      "note": "great angle, do this one"                 // free-text, may be ""
    }
  ]
}
```

Only items the user actually reacted to (a rating or a note) appear in
`reviews`. There's no status field — the file is just an accumulating list. The
page reloads existing reactions from this file, so reacting across sessions
accumulates rather than overwrites.

