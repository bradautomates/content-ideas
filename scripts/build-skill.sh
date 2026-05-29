#!/usr/bin/env bash
# build-skill.sh — package the content-ideas skill as a claude.ai-upload-ready
# .skill file. Usage: bash scripts/build-skill.sh  (run from anywhere)
#
# Produces dist/content-ideas.skill, a zip with a single top-level `content-ideas/`
# directory containing SKILL.md, references/, assets/, and the scripts/ runtime.
# claude.ai's skill upload has a 200-file cap; the zip -d strips below keep the
# bundle lean. The Claude Code / Codex plugin installs use the full repo git
# archive instead (see .gitattributes), so this script only shapes the web bundle.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "error: working tree is dirty; commit or stash before building" >&2
  exit 1
fi

mkdir -p dist
OUT="dist/content-ideas.skill"
rm -f "$OUT"

# Archive only the skill subtree, flattened under a single content-ideas/ dir so
# SKILL.md sits at the top level of the bundle (what claude.ai expects).
git archive --format=zip --prefix=content-ideas/ --output="$OUT" HEAD:skills/content-ideas

# Strip dev/runtime cruft the claude.ai bundle does not need. (* matches '/'.)
zip -d "$OUT" \
  "content-ideas/*__pycache__*" \
  "content-ideas/*.pyc" \
  "content-ideas/scrape_err.log" \
  > /dev/null 2>&1 || true

COUNT=$(unzip -l "$OUT" | tail -1 | awk '{print $2}')
SIZE=$(du -h "$OUT" | cut -f1)

if [ "$COUNT" -gt 200 ]; then
  echo "error: $COUNT files in zip, claude.ai's cap is 200" >&2
  echo "       tighten the zip -d excludes in this script" >&2
  exit 1
fi

SKILL_MD_COUNT=$(unzip -l "$OUT" | grep -c "content-ideas/SKILL.md" || true)
if [ "$SKILL_MD_COUNT" -ne 1 ]; then
  echo "error: expected exactly one SKILL.md, found $SKILL_MD_COUNT" >&2
  exit 1
fi

echo "built $OUT ($COUNT files, $SIZE)"
echo "upload via the claude.ai skill UI (Settings → Capabilities → Skills)"
