---
name: content-strategy
user-invocable: false
description: >
  Turn content research into actionable content plans. Covers title and angle
  generation, differentiator articulation, hook crafting, funnel positioning
  (TOFU/MOFU/BOFU), CTA alignment, repurposing angles, and video brief
  generation. Use when generating content ideas from feed data, planning video
  concepts, creating briefs from outlier content, suggesting hooks or angles,
  classifying content by funnel stage, recommending CTAs aligned to business
  goals, or adapting content across platforms. This skill handles the
  generative/planning side — for engagement scoring, outlier detection, and
  content classification, those capabilities exist separately.
---

# Content Strategy

Domain knowledge for turning content research into actionable plans. This
skill takes what performed well (outliers, competitor posts, trending topics)
and helps create YOUR version — differentiated, strategically positioned, and
tailored to the user's brand context.

The core insight: the gap between "interesting content exists" and "I know
what to make" is where most creators stall. A feed of 50 items is useless
if none of them are translated into a concrete plan the user can act on.
This skill bridges that gap.

**Taste memory is the taste signal.** The user's evolving content taste lives
in your project memory (auto-memory), not in a file — recall it before
recommending. It accumulates from the user's reactions to past feeds: topics
they gravitate toward, formats they prefer, creators they save, angles that
resonate, and what doesn't land. Engagement metrics measure audience behavior;
taste memory measures *this user's* behavior. Recommendations that align with
recalled taste are worth more than engagement alone.

---

## Usage Context

This skill generates full production briefs — complete video briefs with
title, angle, differentiator, hook, funnel + CTA, and repurposing angles.
Actionable enough to start scripting from. Used when generating content
ideas from feed data, planning video concepts, or producing briefs from
any command or conversation.

---

## Title & Angle Generation

The difference between a topic and a content angle is the difference between
"budgeting tips" and "I tracked every dollar I spent for a year — here's the
$4,000 leak I never saw coming." Topics are generic.
Angles are specific, opinionated, and rooted in the creator's perspective.

### The Angle Principle

Never repackage the same topic. Create YOUR version:

- **What do you know that the original creator doesn't?** (expertise depth)
- **What have you experienced that the audience hasn't seen?** (unique access)
- **What do you believe that contradicts the original?** (contrarian take)

If you can't answer at least one of these, the content isn't differentiated
enough to justify making.

### Deriving Angles from Brand Context

When `brand/profile.md` is available, use these fields to generate angles:

| Brand Context Field | How It Shapes the Angle |
|--------------------|-----------------------|
| **Niche** | Sets the lens — "as someone who's coached 200 first-time marathoners..." |
| **Content pillars** | The topic should connect to at least one pillar |
| **Content goal** | Lead gen angles differ from brand building angles |
| **Audience** | Enterprise audience wants different framing than hobbyists |
| **Taste memory** | Recalled auto-memory taste signals — preferred topics, formats, angles |

Use recalled taste memory to bias angle selection toward what this user
actually gravitates toward. An angle that aligns with learned preferences is
more likely to resonate than one based on engagement data alone.

Without brand context, angles stay generic. Flag this: "Angle is general —
build a brand profile in `brand/profile.md` for personalized angles."

---

## Differentiator Articulation

A differentiator is the specific reason the user's version of this content
would be better or different than what already exists. Three types:

### Expertise Depth

The user knows more about this topic than the original creator. They can go
deeper, show edge cases, demonstrate production-grade implementation instead
of a demo.

**Signal phrases:** "Unlike the surface-level version, you can show...",
"Your experience with [specific technology] means you can demonstrate...",
"The original skips [critical detail] that your audience needs."

### Unique Access / Experience

The user has done something the audience hasn't seen. Real client work,
production deployments, specific results with numbers.

**Signal phrases:** "You've actually built this for clients...", "Your
[case study / project] is the proof point...", "You can show real results
where the original only shows a demo."

### Contrarian Perspective

The user disagrees with the original or sees a risk/angle others miss.

**Signal phrases:** "The original misses [critical concern]...", "Your
take is that [contrarian position]...", "Everyone is covering the upside —
you can cover the risk."

### Anti-Cannibalization

When `brand/my-content.md` exists, every new angle MUST be checked against
the Topics Covered table. If the user already covered a topic, the angle
must have an explicit differentiator. Valid differentiators:

- **More depth** — the original was a surface-level overview, this goes deep
- **Different format** — covered as a tutorial, now doing a reaction/debate
- **Updated** — original is outdated, new data/tools/changes warrant a refresh
- **Responding to feedback** — audience comments requested a specific angle
- **Different platform** — covered on YouTube, now adapting for X/LinkedIn

**Invalid:** "Same topic, better execution." If the only differentiator is
"I'll do it better this time," it's not differentiated enough. Drop the idea
or find a genuine angle shift.

When recommending a topic the user already covered, explicitly note it:
"You covered this on {date} — '{title}' ({Nx avg}). This angle differs
because {specific reason}." If the original performed well (>1.5x avg),
the bar for re-covering is higher — the audience already got value from
the first version.

### When Brand Context Is Unavailable

If no `brand/profile.md` exists, differentiator articulation is limited to
generic framing: "Your version could go deeper on...", "A practitioner
perspective would add..." Flag the gap explicitly rather than guessing at
what makes the user unique.

---

## Hook Crafting

Hook crafting generates new hooks for a specific content idea. This is
different from hook *classification* (identifying what mechanism an existing
hook uses) — crafting starts from the content angle and produces opening
lines the user can use.

### Process

1. **Start from the angle**, not the topic. The hook should reflect what
   makes YOUR version different.
2. **Choose a mechanism** that fits the content type. Bold claims work for
   contrarian takes. Curiosity gaps work for tutorials. Transformation
   previews work for case studies.
3. **Write 2-3 variants** using different structural forms. A bold claim as
   a statement, a question, and a command gives the user options.

### Formula Multiplication

Generate 3+ structural variants from one hook — the same mechanism expressed
through different forms:

- **Statement:** "SEO is dead."
- **Command:** "Stop investing in SEO."
- **Question:** "What if SEO is actually dead?"
- **Conditional:** "If you're still relying on SEO, you're already behind."

Statements and commands account for ~70% of top-performing hooks. Start there.

### Platform-Specific Hook Adaptation

The same hook needs different execution per platform:
- **YouTube:** First 5-8 seconds determine retention. The hook IS the thumbnail + title + opening line working together.
- **X:** The hook is the entire tweet or the first line before "Show more."
- **Instagram/TikTok:** Visual + text overlay in the first 1-3 seconds. The spoken hook often differs from the caption.
- **LinkedIn:** The first 2-3 lines before the "see more" fold. If they don't click, the algorithm buries it.

---

## Funnel Positioning

Categorize content by funnel stage to drive CTA selection and help balance
the content mix across awareness, trust, and conversion.

| Stage | Purpose | Classification Signals | Content Characteristics |
|-------|---------|----------------------|------------------------|
| **TOFU** (Top) | Awareness / reach / authority | Trending topic, broad appeal, high search volume, news reaction, bigger-picture positioning | Hot takes, trend reactions, "X is replacing Y" narratives, broad how-tos, industry commentary. Audience: anyone in the niche |
| **MOFU** (Middle) | Consideration / trust / expertise | Speaks to specific ICP, demonstrates implementation skill, educational depth, qualifies audience | Tutorials, walkthroughs, contrarian takes that filter audience, prescriptive frameworks, "how to build X for Y role". Audience: potential buyers/clients |
| **BOFU** (Bottom) | Conversion / proof / objection removal | Case study, testimonial, measurable results, before/after with real numbers, social proof | Client stories, anonymized case studies, "I saved X company Y hours", client interviews, ROI breakdowns. Audience: people ready to buy |

### Classification Logic

Assign by primary intent:

- **TOFU** — rides a trend, broad appeal, high potential impressions, no specific buyer qualification
- **MOFU** — teaches a specific skill, addresses a specific role's pain point, demonstrates expertise that builds trust
- **BOFU** — shows proof/results, tells a client story, provides social proof, removes purchase objections

If an idea spans two stages, classify by the dominant signal and note the
secondary stage. Most content should skew TOFU/MOFU — BOFU is lower volume
but higher conversion.

---

## CTA Alignment

### CTA Types

| Type | Text Pattern | When It Works |
|------|-------------|---------------|
| **follow** | "Follow for more [topic]" | Growing audience, series content |
| **save** | "Save this for later" | Reference content, lists, tutorials |
| **share** | "Send this to someone who..." | Relatable content, useful tips |
| **comment** | "Drop a [emoji] if you agree" | Engagement boosting |
| **link** | "Link in bio" | Conversion, lead gen |
| **next-video** | "Part 2 coming" / "Follow for part 2" | Series hooks, retention |

### CTA by Funnel Stage

| Stage | Primary CTAs | Goal |
|-------|-------------|------|
| TOFU | Follow, subscribe, newsletter signup | Capture attention into owned audience |
| MOFU | Book a call, join workshop, free consultation | Move from audience to prospect |
| BOFU | Direct sales, "let's work together", proposal link | Convert prospect to client |

### CTA Placement

| Placement | Effect |
|-----------|--------|
| **End** (last 3-5 seconds) | Standard. Works for tutorials and stories. |
| **Middle** (during value delivery) | Higher conversion — viewer is engaged but not done. |
| **Caption only** (not spoken) | Non-intrusive. Works for entertainment content. |
| **Multiple** (caption + spoken + text) | Aggressive but effective for conversion-focused content. |

### Platform CTA Conventions

| Platform | Most Effective CTA Types |
|----------|------------------------|
| TikTok | Follow + comment + save. "Part 2" hooks drive follows. |
| Instagram | Save + share. Saves boost Explore distribution. |
| YouTube | Subscribe + like. Algorithm weights subscriber engagement. |
| X | Bookmark + retweet. "Bookmark this thread" is high-signal. |

### Brand-Context-Aware CTAs

When `brand/profile.md` includes a content goal, align CTA suggestions to it:

| Content Goal | CTA Lean |
|-------------|---------|
| Lead generation | "Book a [consultation type]", "DM me [keyword]" |
| Brand building | "Follow for more [topic]", "Subscribe" |
| Product/course sales | "Link in bio to [product]", "Join the waitlist" |
| Email list growth | "Comment [KEYWORD] and I'll send you [lead magnet]" |

---

## Repurposing Angles

Generate platform-specific adaptation angles for content ideas, particularly
those sourced from text-first platforms (X, Reddit) heading to video/visual
platforms.

### Per-Angle Structure

| Component | Description |
|-----------|-------------|
| **Target platform** | From user's target platforms in `brand/profile.md` |
| **Format** | Best-performing format for that platform from research data |
| **Hook adaptation** | Adapt the source hook to the target platform's conventions |
| **What to add/change** | Platform-specific adjustments (length, visual style, CTA) |

### Platform-Specific Adaptation Rules

| From X Tweet | To TikTok | To Instagram | To YouTube |
|-------------|-----------|-------------|-----------|
| Thread | Talking-head summarizing key points (30-60s) | Carousel with one point per slide | Long-form deep dive or Shorts version |
| Hot take | Stitch/reaction format | Bold-claim reel with text overlay | Community post or Shorts |
| Tutorial thread | Step-by-step screen recording (15-60s) | Tutorial reel or carousel walkthrough | Full tutorial video (5-15 min) |
| Data/stat | "Did you know" format with stat as hook | Infographic carousel | Data breakdown video with visuals |
| Bookmark-bait list | "Save this" listicle with quick cuts | Carousel list (one item per slide) | Compilation or ranked list video |

### Angle Quality

A good repurposing angle matches the target platform's dominant format, adapts
the hook (not copy-pastes it), adds platform-appropriate value, and
acknowledges different audience expectations. "Post it on TikTok" is not an
angle. "30-second talking-head with the stat as the opening hook, save CTA" is.

---

## Brief Generation

A video brief is the bridge between "this is an interesting piece of content"
and "I know what to make." Briefs should be actionable enough to start
scripting from.

### Video Brief Format

Each brief contains:

| Component | What It Answers | How to Generate |
|-----------|----------------|----------------|
| **Video concept** | What am I making? | Title + angle from Title & Angle Generation |
| **Why now** | Why should I make this today? | Reference specific data from the feed — engagement numbers, competitor activity, news timing, recalled taste |
| **Your differentiator** | Why will mine be better? | From Differentiator Articulation — expertise, access, or contrarian angle |
| **Suggested hook** | How do I open? | From Hook Crafting — 1-2 specific opening lines |
| **Funnel position + CTA** | Where does this fit in my strategy? | From Funnel Positioning + CTA Alignment |
| **Repurpose as** | What else can I make from this? | From Repurposing Angles — platform-specific adaptations |

### Taste-Informed Briefs

Recall the user's taste memory before generating briefs — accumulated taste
signals (topics, formats, creators, angles the user gravitates toward). Use it
for:

- **Selection:** A topic that aligns with learned preferences is a stronger
  pick than one based on engagement alone.
- **"Why now":** Taste can justify timing — "This aligns with a pattern
  you've been consistently drawn to."
- **Angle shaping:** If taste signals show the user prefers a specific format
  or angle type, shape the brief to match.

### Briefs from Own Audience Requests

When `brand/my-content.md` contains Audience Requests, demand from the
user's own audience is the highest-confidence signal for brief generation.
These are people who already follow and engage with the user asking for
specific content.

**Why it's the strongest signal:** Competitor comment demand says "someone's
audience wants this." Own audience demand says "YOUR audience wants this."
The conversion from idea to engaged viewer is nearly guaranteed.

**Brief adjustments for own-audience requests:**
- **Video concept** — derived directly from the request, not abstracted
- **Why now** — cite the request: "Your audience asked for this {N} times
  across recent posts. Top comment: '{quote}' ({engagement})"
- **Hook** — can reference the request directly: "In my last video on X,
  the most common question was... Here's the answer."
- **Differentiator** — writes itself. The audience asked YOU specifically.
  Your existing content is the context they're building on.

### Briefs from Audience Signals

When an idea is driven by comment demand or a bookmarked post, the brief
shifts to foreground the demand signal:

- **Video concept** — derived from the demand signal (the comment's request
  or the bookmarked post's angle), not just the source post's topic.
- **Why now** — cite the specific demand. For comments: "Direct audience
  demand: [quote] received [N likes]. [N similar comments across the feed]."
  For bookmarks: "You bookmarked this — here's the angle that differentiates
  your version."
- **What the audience is asking for** — the actual comment quote(s) with
  engagement numbers, or the bookmark context showing why you saved it.
  This field makes the demand visible and concrete.
- **Differentiator** — why the user is the right person to answer this
  specific request. Reference brand context.
- **Suggested hook** — can address the demand directly: "Someone asked me
  [paraphrased question]. Here's the answer..." or "I bookmarked this post
  last week and it's been living in my head. Here's why I think they got
  it half right."

Not every idea has an audience signal. Outlier-based ideas may derive their
"Why now" from engagement data and timing. But when comment or bookmark
signal exists, foreground it — it's the strongest evidence an idea has
real demand.

### Quality Bar

A brief passes the quality bar if:
- The user could hand it to a scriptwriter and they'd know what to write
- The angle is specific enough that two creators given the same brief would
  make noticeably different content
- The hook is a real opening line, not a description of what the hook should do
- The CTA connects to the user's actual business goal, not a generic "subscribe"

### Without Brand Context

Briefs without brand context are weaker but still useful. The concept and
hook can be generic; the differentiator defaults to "practitioner depth" or
"hands-on demo"; the CTA stays generic. Flag what's missing: "Brief is
general — brand context from `brand/profile.md` would sharpen the angle and CTA."

---

## Key Principles

- **Generate, don't classify.** This skill creates new hooks, titles, angles,
  and briefs. Classification of existing content is a separate concern.
- **Brand context makes everything better.** Every section works without
  `brand/profile.md`, but the output is significantly sharper with it.
  Always note when brand context would improve the result.
- **Specificity over safety.** "knife skills tutorial" is safe but useless.
  "I had a pro chef grade my knife skills — here's everything I'd been doing
  wrong" is specific and actionable. Push toward specificity.
- **One brief should be enough.** The user shouldn't need to ask follow-up
  questions to start producing. If they do, the brief was too vague.
- **Taste memory is taste.** Your recalled taste memory captures what this
  user gravitates toward — not what audiences like, what *they* like. When
  signals exist, they should visibly shape recommendations. A pick that
  connects to a learned pattern is worth calling out.
