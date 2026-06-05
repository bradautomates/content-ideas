---
name: content-ideas
version: "2.2.0"
description: >
  Your For You page for content creators. Scrapes tracked competitors across
  social media platforms, scores what's performing, and turns it into actionable, differentiated content ideas backed
  by real engagement data. Use this whenever the user wants competitor/creator
  research, a content feed or "for you" page, trending-topic ideas in their
  niche, to see what's working on social, to track what creators are posting,
  or to generate video/post briefs from what's performing — even if they don't
  say "find ideas." First run walks through setup.
argument-hint: "[topic filter]"
user-invocable: true
allowed-tools: Bash, Read, Write, AskUserQuestion
metadata:
  requires:
    env:
      - SCRAPECREATORS_API_KEY
    bins:
      - python3
---

# content-ideas

Your For You page. Scrapes every platform where your tracked creators publish,
scores what's performing, and turns it into content ideas you can act on.
Designed to run daily — each run creates a dated feed under `$CONTENT_HOME/research/`.

The output is a single self-contained HTML page (two tabs: **Posts** — one
sortable, filterable feed merging tracked-account posts and discovered niche
outliers — and **Ideas**) that you can open in a browser, react to, and
keep. Reactions are captured for future personalization.

## Resolve the skill directory

Everything this skill runs lives under its own folder. The skill installs the
same way on Claude Code and Codex, so resolve `SKILL_DIR` against both plugin
caches (and a plain repo checkout) once, before anything else:

```bash
# 1) Codex plugin cache, or a repo cloned into ~/.codex/skills/ (latest wins on upgrade).
SKILL_DIR="$(ls -d "$HOME/.codex/plugins/cache/"*/content-ideas/*/skills/content-ideas/ "$HOME/.codex/skills/"*/skills/content-ideas/ 2>/dev/null | sort -V | tail -1)"
SKILL_DIR="${SKILL_DIR%/}"

# 2) Claude Code plugin cache.
if [ -z "$SKILL_DIR" ] || [ ! -f "$SKILL_DIR/scripts/scrape.py" ]; then
  CLAUDE_ROOT="$(ls -d "$HOME/.claude/plugins/cache/content-ideas/content-ideas/"*/ 2>/dev/null | sort -V | tail -1)"
  CLAUDE_ROOT="${CLAUDE_ROOT%/}"
  [ -n "$CLAUDE_ROOT" ] && [ -f "$CLAUDE_ROOT/skills/content-ideas/scripts/scrape.py" ] && SKILL_DIR="$CLAUDE_ROOT/skills/content-ideas"
fi

# 3) Plugin root passed by the host, or a repo checkout / local dev.
if [ -z "$SKILL_DIR" ] || [ ! -f "$SKILL_DIR/scripts/scrape.py" ]; then
  for dir in "${CLAUDE_PLUGIN_ROOT:-}/skills/content-ideas" "${CLAUDE_PLUGIN_ROOT:-}" "${GEMINI_EXTENSION_DIR:-}/skills/content-ideas" "./skills/content-ideas" "."; do
    [ -n "$dir" ] && [ -f "$dir/scripts/scrape.py" ] && SKILL_DIR="$dir" && break
  done
fi

echo "$SKILL_DIR"
```

If you can already see this file's path, just use its directory. The two
scripts you'll call are `$SKILL_DIR/scripts/scrape.py` and
`$SKILL_DIR/scripts/generate_feed.py`. The renderer template is
`$SKILL_DIR/assets/for-you-template.html` (the generator finds it automatically).

## Resolve the project (multi-project mode)

This skill supports two operating modes:

- **Single-project** (legacy behavior for users who installed before
  multi-project landed) — one `brand/`, one `~/.config/content/.env`.
  Everything lives under one `CONTENT_HOME`.
- **Multi-project** (default for new installs) — multiple isolated
  projects, each with its own brand/, tracked accounts, research
  history, and API key. Selected via a slug arg:
  `/content-ideas <slug>` or `/content-ideas` (defaults to last-used
  slug). Fresh installs always start in this mode via Step 0a–0b
  (install-path + first-project-slug setup).

Detect mode by checking `$ARGUMENTS`:

1. **Parse the first token** of `$ARGUMENTS`. If it's a single identifier
   (alphanumeric, dashes, underscores — no spaces, no quotes, no JSON
   braces), treat it as a candidate slug. Pop it from arguments before
   passing the remainder downstream.
2. **If no slug given, look for** `~/.config/content/last-project` and
   read its contents as the slug (this is how bare `/content-ideas`
   defaults to the user's last project).
3. **If neither yields a slug AND `CONTENT_IDEAS_HOME` is set** (env var
   or `.env` file), you're a fresh-install user mid-Step-0 — go to
   Step 0b to name the first project.
4. **If neither yields a slug AND no `CONTENT_IDEAS_HOME` either** —
   you're in legacy single-project mode (or a truly fresh install that
   needs the full Step 0 flow). Skip straight to "Resolve the content
   home" below; Step 0 will sort it out.

When you resolve a slug, **announce it explicitly to the user**:
`Using project: <slug>` so a wrong-default catches their eye immediately.
A bare-call default that doesn't match the user's intent is the riskiest
UX failure here.

Then locate the wrapper that drives multi-project routing (optional —
the skill works without it, just w/o the auto-credit-logging). Resolve
`$CONTENT_IDEAS_HOME` first (env var → `.env` file value → default
`~/Documents/Content` — see `env.py:content_ideas_home()`). Then check
these wrapper paths in order:

1. `$CONTENT_IDEAS_HOME/bin/scrape.sh` (resolved as above)
2. `$HOME/ObsidianVaults/mise/content-ideas/bin/scrape.sh` (vault convention)
3. `$HOME/Documents/Content/bin/scrape.sh` (Content-dir convention)
4. `$CONTENT_HOME/bin/scrape.sh` (single-project wrapper, if `CONTENT_HOME` is set)

The first match wins. Capture its directory as `CI_ROOT` (= `$(dirname
$(dirname <wrapper>))`). Per-project state then lives at:

```
CONTENT_HOME = $CI_ROOT/projects/<slug>/
KEY_FILE     = ~/.config/content/<slug>.env
```

If no wrapper exists, you're in single-project mode regardless of slug —
warn the user and fall back to the single-project flow.

## Resolve the content home

(Multi-project mode resolved this in the previous section. Skip ahead to
Step 0 unless you're falling back to single-project.)

In **single-project mode**, all persistent files this skill reads and
writes — the `brand/` profile and the dated `research/` runs — live under
one stable base, **never** the current working directory. The skill runs
daily and is invoked from anywhere, so the base must be the same every
time or it loses the profile and the run history. Resolve it once and
capture the concrete path:

```bash
CONTENT_HOME="${CONTENT_HOME:-$HOME/Documents/Content}"
mkdir -p "$CONTENT_HOME/brand" "$CONTENT_HOME/research"
echo "$CONTENT_HOME"
```

Throughout this guide every `brand/...` and `research/...` path is relative to
`$CONTENT_HOME` (so `brand/profile.md` means `$CONTENT_HOME/brand/profile.md`).
**Use the printed absolute path for every Read/Write of those files** — the
file tools don't expand shell variables, so writing a bare `brand/profile.md`
would land it in the wrong directory. (Credentials stay separate, in
`~/.config/content/.env` for single-project, or `~/.config/content/<slug>.env`
for multi-project.) The scrape/generate scripts read `CONTENT_HOME`
themselves, so a relative `research/{today}` passed to them resolves here too.

---

## Step 0: First-run setup (or new-project setup)

**Run this before anything else, even if the user gave a topic.**

This step has 7 substeps (0a–0g) covering: install-path choice, project-slug naming, existing-install detection, API-key collection, manual-config alternative, brand-profile bootstrap from the user's own channels, and competitor-tracker seeding.

Detection — if `~/.config/content/.env` exists AND `<slug>.env` exists for the resolved project AND `SETUP_COMPLETE=true`, skip Step 0 entirely and go to Step 1. Otherwise, **see `references/first-run-setup.md` for the full setup flow** (substeps 0a–0g + the `AskUserQuestion` prompts, slug-validation rules, and brand-profile scrape pattern).

## Step 1: Load context

### 1a. Ingest the previous run's feedback into taste memory

Before anything else, fold the **last** run's reactions into your memory — this
is what makes each run better than the one before. List the dated subfolders of
`$CONTENT_HOME/research/` (`YYYY-MM-DD`) and take the most recent one. If it has a
`feedback.json`, read it and distill each entry in `reviews[]` (▲ "more like
this" / ▼ "less" / a note) into the *generalizable* taste signal, not the
one-off:

- "▲ on three contrarian takes in the user's niche" → "gravitates toward
  contrarian takes"; "▼ on listicles" → "listicle formats don't land." A
  note often states the reason directly — use it.
- **Record these to your project memory** (the auto-memory you maintain) as the
  user's content taste — the same place 1b recalls from. Update an existing
  taste note rather than duplicating it; let a single ▼ inform, not override, an
  established preference. Don't record one-off reactions with no pattern,
  anything already obvious from `brand/profile.md`, or post/run specifics (those
  live in `research/`). Taste only.

If there's no prior dated folder, no `feedback.json`, or no reactions in it,
skip silently. If auto-memory isn't available in this environment, skip too —
the reactions stay in `feedback.json` for whenever it is. (The current run's
reactions are ingested by the *next* run, the same way — there's no end-of-run
distillation step.)

### 1b. Recall taste and load brand context

Read whatever brand context exists (all optional — degrade gracefully):
- `brand/profile.md` — niche, pillars, search terms, content goal, audience
- `brand/tracked-accounts/*.md` — tracked creators per platform
- `brand/my-content.md` — the user's own content performance + audience requests

**Recall the user's content taste from your memory.** This skill stores an
evolving taste profile in your project memory (the auto-memory you maintain). Before generating ideas, recall what you know about what this
user gravitates toward — preferred topics, formats, angles, creators they keep
saving, and what doesn't land for them. If relevant taste signals are already
surfaced in context, use them; if not and memory is available, look for taste
notes tagged for this skill. This is the single most important personalization
input: engagement metrics measure what *audiences* like, taste memory measures
what *this user* likes. If auto-memory isn't available, fall back to engagement
signals alone (and to `brand/my-content.md` if present).

If there are no tracked accounts and no topic filter, ask for handles or a
topic before scraping.

### 1c. Refresh your own content (`my-content.md`)

Before generating ideas, bring `brand/my-content.md` up to date — this is the
per-run counterpart to the one-time build in Step 0f, and it's what keeps
anti-cannibalization and the "your audience is asking for" banner honest as the
user keeps posting. (`my-content.md` is declared *updated each run* in
`FILE-SCHEMAS.md`; this is the step that does it.)

Take the user's own handles from the `## My Social Profiles` section of the
`brand/profile.md` you just loaded, normalize them into the `{platform: [handle]}`
shape, and re-scrape them over a window wide enough to catch their own cadence
(`--days 30` — a creator's own posts are sparser than the merged competitor
feed, but keep it "recent," not the 90-day profile build from Step 0f):

```bash
python3 "$SKILL_DIR/scripts/scrape.py" \
  '{"x": ["me"], "youtube": ["@mychannel"]}' \
  --pillars "<pillars from profile.md>" --days 30
```

The scraper already pulls comments on the top posts, so the returned data
carries the audience replies you need. Rewrite `brand/my-content.md` from it per
the schema in `FILE-SCHEMAS.md` (performance summary, what's working / not,
topics covered, and audience requests distilled from the comments) — it's
replaced, not appended. Use this fresh version, not the copy you read in 1b, for
the rest of the run.

**Best-effort — never block the feed.** If `profile.md` has no own handles (the
user skipped profile setup), or the scrape returns nothing or errors, keep the
existing `my-content.md` and continue. This refresh is an enrichment, not a gate.

---

## Step 2: Create the daily run folder

List existing dated subfolders of `$CONTENT_HOME/research/` (`YYYY-MM-DD`). The most recent
one that is **not** today is the last-run date — pass it as `--since` in Step 3
so the scrape only keeps posts on/after that day. If there are no prior dated
folders, there's no `--since`.

Either way, the scraper enforces a **recency window** so the daily feed never
surfaces stale posts: by default it keeps only the **last 7 days** (`--days`).
`--since` can only *narrow* that window, never widen it — so first runs and
long-gap runs are both bounded to a week by default. (The script's hard cap is
90 days; for the daily feed keep it tight — a month at most. The 90-day window
is for one-off profile builds in Step 0f, not the daily feed.)

Create `$CONTENT_HOME/research/{today}/`.

**If `$CONTENT_HOME/research/{today}/feed-data.json` already exists**, ask whether to:
- **Refresh** — re-pull and rebuild (reuse the same `--since` / `--days`)
- **Expand** — widen the window: drop `--since` and/or raise `--days` (keep the
  feed within ~30 days) when the user wants more than the last week
- **View** — just (re)open the existing feed (skip to Step 6)

---

## Step 3: Scrape competitors

Build a JSON object mapping each platform to its tracked handles. Pass content
pillars (from `brand/profile.md`, or the user's niche/topic) via `--pillars` so
the script scores relevance, and the last-run date via `--since`. Leave `--days`
at its default (7) unless the user asks for a wider window, then raise it (max
31).

**Wrapper-first invocation.** If a wrapper was discovered in the "Resolve
the project" step (multi-project mode) OR if `$CONTENT_HOME/bin/scrape.sh`
exists (single-project convention), prefer it over the bare `scrape.py`.
Wrappers add per-user logging (credits tracking, run-log appending,
threshold alerts) that the base script intentionally doesn't know about.

Multi-project mode passes the slug as the first arg; the wrapper resolves
`CONTENT_HOME` + key from that. Single-project wrappers don't take a slug.

```bash
# Multi-project wrapper (slug as first arg, wrapper handles paths + key):
"$CI_ROOT/bin/scrape.sh" "<slug>" \
  '{"x": ["h1","h2"], "instagram": ["h3"], "youtube": ["@h4"]}' \
  --pillars "<the user's content pillars>" \
  --since 2026-04-15 \
  --days 7

# Single-project wrapper (no slug; uses $CONTENT_HOME + ~/.config/content/.env):
"$CONTENT_HOME/bin/scrape.sh" \
  '{"x": ["h1","h2"], "instagram": ["h3"], "youtube": ["@h4"]}' \
  --pillars "<the user's content pillars>" \
  --since 2026-04-15 \
  --days 7

# Bare fallback (no wrapper at all):
python3 "$SKILL_DIR/scripts/scrape.py" \
  '{"x": ["h1","h2"], "instagram": ["h3"], "youtube": ["@h4"]}' \
  --pillars "<the user's content pillars>" \
  --since 2026-04-15 \
  --days 7
```

**Wrapper exit codes (multi-project mode)** that you should handle in
the calling flow rather than treating as generic failures:
- `3` — project dir doesn't exist. **Trigger new-project setup** (Step 0
  flow), then retry the wrapper call.
- `4` — API key file missing for this slug. Ask the user for the key,
  write `$KEY_FILE`, retry.
- `5` — key file present but `SCRAPECREATORS_API_KEY` empty. Same fix
  as `4`.
- Anything else (including `1`, `2`) — surface the wrapper's stderr to
  the user and stop.

Tell the user this takes a few minutes; progress streams to stderr. The script
fetches all accounts in parallel, **drops anything outside the recency window**,
scores engagement and relevance, flags outliers, and pulls comments/transcripts
on top posts. It returns:

```json
{ "results": { "x": { "h1": [ {post}, ... ] } }, "errors": [] }
```

Each post has `text`, `url`, `author`, `date`, `platform`, `engagement`,
`score` (weighted), `relevance` (0–1 vs pillars), `baseline` (Nx the account
average), `outlier` (bool), and — on top posts — `comments` / `transcript`.

**On errors:** report which accounts failed and proceed with what came back.

### Ad-hoc: fetch specific posts by URL

When the user hands you specific post URLs (a competitor's viral post, a link
they saw), use URL mode instead of profile mode. It returns a flat `[post]`
array with the same shape:

```bash
python3 "$SKILL_DIR/scripts/scrape.py" urls "https://x.com/u/status/1" "https://www.tiktok.com/@u/video/2" --pillars "..."
```

---

## Step 4: Review the scored data

The script pre-computes `score`, `baseline`, `relevance`, and `outlier`.
Identify the top-performing posts and the topics/themes/angles driving
engagement — especially high-relevance ones. This is the raw material for the
Ideas tab.

---

## Step 5: Build the feed

Two tabs. Everything shown has proven engagement. Build a `FEED_DATA` object
and write it (Step 6). Field-by-field structure is in the plugin's
`FILE-SCHEMAS.md` (`feed-data.json`).

**Tab 1 — Posts.** One flat `posts[]` array merging two sources into a single
sortable, filterable feed (the page handles sorting and grouping client-side —
do **not** pre-sort or pre-group):

- *Tracked-account posts* — every post from tracked accounts (no engagement
  gate). Set `performance` / `performanceDirection` vs the account baseline
  (e.g. `"+210% vs baseline"`, `"up"`).
- *Discovered niche outliers* — statistical outliers (`outlier: true`, z-score
  2+, or baseline 2x+). Set `zScore` and a `why` line.

  Per post, regardless of source, provide: a 1–3 sentence `text` summary,
  `url`, `handle` + `displayName` (creator filter), `platform`, an `engagement`
  object, a hook callout when notable, and the two fields that make the feed
  work — `timestamp` (ISO 8601, drives **Recent** sort + relative time) and
  `sortValue` (numeric total engagement/reach, drives the default **Popular**
  sort). A post is flagged as an outlier (intensity-scaled badge + accent bar)
  whenever it has a `zScore` **or** `performanceDirection: "up"` — so a tracked
  post that beat its baseline shows as an outlier too.

**Tab 2 — Ideas.** The one place you editorialize (label it as AI suggestion).
Generate up to 10 ideas, each with: a specific differentiated angle, real
evidence from competitor performance, and clear differentiation from what
competitors already covered.

For the generative craft — turning a topic into a differentiated angle, writing
hooks, classifying funnel stage (TOFU/MOFU/BOFU), aligning CTAs, repurposing
across platforms, and producing a full brief — **read
`references/content-strategy.md`**. The short version to keep in mind while
building this tab:

- **Make YOUR version, never repackage.** A good angle answers at least one of:
  what do you know the original creator doesn't (expertise), what have you done
  the audience hasn't seen (access), or where do you disagree (contrarian)?
- **Anti-cannibalization.** When `brand/my-content.md` exists, don't re-pitch a
  topic the user already covered unless the angle has a genuine differentiator
  (more depth, different format, an update, a response to feedback). Note prior
  coverage explicitly.
- **Own-audience demand wins.** Requests from the user's own audience
  (`brand/my-content.md`) outrank competitor signals — foreground them in the
  brief's "why now."
- **Taste memory biases selection.** An idea that aligns with the taste signals
  you recalled in Step 1 (topics/formats/angles this user gravitates toward)
  is a stronger pick than one justified by engagement alone — and worth calling
  out ("this fits a pattern you keep coming back to"). Conversely, deprioritize
  anything that matches a recorded "doesn't land" signal.

---

## Step 6: Write and open the feed

Write the feed data to `$CONTENT_HOME/research/{today}/feed-data.json` — a JSON object with
keys `meta`, `posts`, `ideas` (see `FILE-SCHEMAS.md`).
Do **not** write HTML yourself; the generator embeds this JSON into the
template.

Then render it. Default to the live server (lets the user react to items, which
saves to `feedback.json` for future personalization):

```bash
python3 "$SKILL_DIR/scripts/generate_feed.py" "$CONTENT_HOME/research/{today}"
```

This starts a local server and **automatically opens the feed in the user's
default browser**. Still hand the user the `http://localhost:<port>` URL the
command prints, so they can reopen it if the tab closes. (Pass `--no-browser` to
suppress the auto-open; the URL is printed either way.) The command runs in the
foreground until the user stops it with Ctrl+C, so run it in the background if
you need to keep working.

In a headless/no-display environment, write a self-contained file instead and
point the user at it (the page lets them download their reactions):

```bash
python3 "$SKILL_DIR/scripts/generate_feed.py" "$CONTENT_HOME/research/{today}" --static
# → $CONTENT_HOME/research/{today}/for-you.html
```

Then present a short text summary (post count, how many are outliers, a couple
of standout posts) and the page location.

---

## Step 7: Offer next steps

The user reacts to the feed in the browser; their reactions save to
`research/{today}/feedback.json` on their own — automatically in server mode,
or via the page's download button in static mode. There's no "done" signal and
nothing for you to read or distill now: the file just accumulates reactions,
and the **next** run folds them into taste memory at Step 1a. This keeps the
workflow simple and, crucially, captures reactions the user makes after this
conversation has ended.

Offer to: dig deeper on any idea, add/remove tracked accounts, or rerun with a
different topic focus.

---

## Notes

- **Reactions / feedback → taste memory.** The feed page lets the user mark
  items (▲ more like this / ▼ less / a note) across both tabs. In server
  mode these save to `research/{date}/feedback.json` automatically as the user
  clicks; in static mode the user downloads that file into the run folder. The
  file is just an accumulating list of reactions — no status, no submit step.
  The **next** run reads the previous run's `feedback.json` at Step 1a and
  distills it into your project memory so future runs are personalized — there
  is no taste *file*; taste lives in auto-memory.
- **No API key = no run.** Both profile and URL mode require
  `SCRAPECREATORS_API_KEY` — every platform, including YouTube transcripts, goes
  through ScrapeCreators. If the key is missing, the script returns an error;
  stop and show setup instructions rather than inventing data.
