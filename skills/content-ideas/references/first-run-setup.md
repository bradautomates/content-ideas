## Step 0: First-run setup (or new-project setup)

**Run this before anything else, even if the user gave a topic.**

### 0a. First-ever install — choose where files live

If this is a **truly fresh install** — `~/.config/content/.env` doesn't
exist, no `<slug>.env` files exist in that dir, and `$CONTENT_IDEAS_HOME`
isn't set anywhere — ask the user where they'd like content-ideas to
store the brand profile, tracked accounts, and dated research history.
Otherwise skip this step (an existing install already picked a path).

Show a short note about why this matters, then `AskUserQuestion`:

> Before anything else: where should content-ideas store your files?
> Brand profile, tracked competitors, and the daily research/feed
> outputs live here. Pick somewhere durable — this is the home for
> everything the skill writes, across all projects and all daily runs.

Offer these options:
- `~/Documents/Content/` (default, no decision needed)
- `~/Content/` (top-of-home, shorter path)
- `~/.local/share/content-ideas/` (XDG-compliant, hidden by default)
- Other — paste a path (e.g. inside an Obsidian vault, iCloud Drive,
  Dropbox; great for users who already have a "second-brain" tree)

Expand `~` and create the dir. Write `CONTENT_IDEAS_HOME=<absolute-path>`
to `~/.config/content/.env` (create the dir + file if missing). All
future invocations read this; `env.py:content_ideas_home()` is the
resolver.

This is the install-root. The skill always operates in multi-project mode
from here — even users who'll only ever have one project get a clean
`<install-root>/projects/<slug>/` layout that's trivial to extend later.

### 0b. Name the first project (slug)

After the path is chosen (or on any later invocation against an unknown
slug), prompt for the project slug. `AskUserQuestion`:

> What should we call this project? Pick a short slug — lowercase,
> dashes-not-spaces. This becomes the project identifier you'll pass
> as `/content-ideas <slug>` to invoke this feed specifically. For a
> "just one feed" install, pick whatever fits your brand/persona
> ("my-brand", "my-channel", etc.) — you can rename later by moving
> the dir.

Validate slug shape (alphanumeric + dashes/underscores; reject spaces +
quotes + braces — those collide with the multi-project arg-parser). Set:

```
CONTENT_HOME = $CONTENT_IDEAS_HOME/projects/<slug>/
KEY_FILE     = ~/.config/content/<slug>.env
```

Create `$CONTENT_HOME/brand/tracked-accounts/` and seed
`~/.config/content/last-project` with this slug.

### 0c. Existing-install / new-project detection

If the user invoked the skill against an **existing project**
(`$CONTENT_HOME` + `$KEY_FILE` both already exist for this slug), skip
0d–0g and continue to Step 1. Otherwise — fresh install OR known
`CONTENT_IDEAS_HOME` but unknown slug — continue setup below.

Confirm the slug with the user via `AskUserQuestion` before writing
anything (chance to back out or retype). Then run 0d–0g. All file writes
go to the per-project paths (`$CONTENT_HOME/brand/...`, `$KEY_FILE`).
After setup, continue to Step 1.

### 0d. Welcome + API key

Setup has three quick parts: an API key, **your** profile (built from your own
channels), and the competitors you want to track. Only the key is required —
the rest the skill bootstraps for you and you can refine any time. Nothing to
install; one ScrapeCreators API key covers all four platforms — X, Instagram,
TikTok, and YouTube (including transcripts).

Show this as a normal message, then call `AskUserQuestion` (don't repeat the
welcome inside the modal):

> I turn your social presence into a daily For You feed: I build a profile from
> your own channels, track the competitors you pick, and surface what's
> performing as content ideas backed by real engagement. I just need a
> ScrapeCreators API key (one key covers all four platforms; 100 free calls, no
> card).

`AskUserQuestion` — "Add your ScrapeCreators API key?"
- Open scrapecreators.com to grab a free key
- I'll paste a key now
- Skip for now

If they pick "Open scrapecreators.com", run `open https://scrapecreators.com`,
then ask them to paste the key. When the user pastes a key, write to the
correct path for the mode:

- Single-project: `~/.config/content/.env`
- Multi-project: `$KEY_FILE` (= `~/.config/content/<slug>.env`)

(Create dirs; append, don't clobber other keys):

```
SCRAPECREATORS_API_KEY={key}
SETUP_COMPLETE=true
```

If they skip, write only `SETUP_COMPLETE=true`. In multi-project mode also
write the slug to `~/.config/content/last-project` so bare `/content-ideas`
defaults to this project next time.

### 0e. Manual alternative

If they'd rather configure by hand, tell them to add those two lines to
`~/.config/content/.env`. Offer to write the file if they paste the key here.

### 0f. Build your brand profile

This is what personalizes everything: ideas get framed against *your* niche,
pillars, and goal, and checked against what you've already posted. Build it from
the user's own presence rather than a long questionnaire.

Ask for their own channels (`AskUserQuestion`: "Set up your profile now?" →
**I'll share my handles** / **Skip — I'll add it later**). When they share
handles — free-form across any platforms (`@me` on X, a YouTube channel, a
TikTok, etc.) — normalize them into the `{platform: [handle]}` shape and scrape
them like competitors, but over a much wider window (`--days 90`, the max) so
you characterize their work from a full quarter, not just recent posts:

```bash
python3 "$SKILL_DIR/scripts/scrape.py" \
  '{"x": ["me"], "youtube": ["@mychannel"]}' \
  --pillars "" --days 90
```

From the returned posts (plus comments/transcripts), draft the profile:
- **Niche, Audience, Voice Notes** — infer from recurring topics, framing, tone.
- **Content Pillars** — the 3–5 themes their posts actually cluster into. These
  drive `--pillars` on every future run, so get them right.
- **My Social Profiles** — handle, follower count, bio, and a one-line content-
  style note per platform, taken from the scrape.
- **Target Platforms / Research Channels** — the platforms they're active on.
- **Search Terms** — concrete keywords from their top topics.

Two things you can't scrape — **ask** (`AskUserQuestion`), then fold the answers in:
- **Content Goal** — why they post (lead gen / awareness / growth / thought
  leadership / selling…), where they drive traffic, and what they're promoting.
- **Pillar confirmation** — show the 3–5 pillars you inferred and let them
  edit or confirm before writing.

Write `brand/profile.md` per the schema in `FILE-SCHEMAS.md`. If the scrape
returned enough of their own posts, also write an initial `brand/my-content.md`
(performance summary, what's working, topics covered, and audience requests
distilled from their comments) — this powers anti-cannibalization and the "your
audience is asking for" banner from day one.

**If they skipped** (or there's no API key yet to scrape with), don't block:
build a minimal `brand/profile.md` from a 2–3 question Q&A (niche, rough
pillars, goal), note that re-running setup with a key auto-enriches it, and move
on.

### 0g. Track competitors

Ask who they want to track (`AskUserQuestion`: list them now / skip and use an
example). If they list handles, create `brand/tracked-accounts/{platform}.md`
files per the schema in the plugin's `FILE-SCHEMAS.md`. If they skip, run a
small example so they see the shape, and tell them they can add real
competitors later.

**End of first-run setup.** Then continue with the user's original request.

---