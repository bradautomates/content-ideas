"""Structural contract for the content-ideas skill: files present, frontmatter
valid, template wired to the generator, and the Claude Code + Codex packaging
manifests agreeing. No third-party deps."""

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "content-ideas"


def _json(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


def _skill_version():
    fm = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("\n---\n", 1)[0]
    match = re.search(r'(?m)^version:\s*"([^"]+)"\s*$', fm)
    assert match, "SKILL.md version frontmatter not found"
    return match.group(1)


def _pyproject_version():
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    assert match, "pyproject.toml version not found"
    return match.group(1)


class SkillFilesTests(unittest.TestCase):
    def test_expected_files_exist(self):
        for rel in [
            "SKILL.md",
            "references/content-strategy.md",
            "assets/for-you-template.html",
            "scripts/scrape.py",
            "scripts/generate_feed.py",
            "scripts/lib/__init__.py",
            "scripts/lib/pipeline.py",
        ]:
            self.assertTrue((SKILL / rel).exists(), f"missing {rel}")


class FrontmatterTests(unittest.TestCase):
    def setUp(self):
        self.text = (SKILL / "SKILL.md").read_text()

    def test_has_yaml_frontmatter(self):
        self.assertTrue(self.text.startswith("---\n"))
        self.assertGreaterEqual(self.text.count("\n---\n"), 1)

    def test_has_name_and_description(self):
        fm = self.text.split("\n---\n", 1)[0]
        self.assertRegex(fm, r"(?m)^name:\s*content-ideas\s*$")
        self.assertRegex(fm, r"(?m)^description:")

    def test_user_invocable(self):
        fm = self.text.split("\n---\n", 1)[0]
        self.assertRegex(fm, r"(?m)^user-invocable:\s*true\s*$")

    def test_taste_uses_memory_not_learnings_file(self):
        # Taste was migrated from brand/learnings.md to auto-memory.
        self.assertNotIn("brand/learnings.md", self.text)
        self.assertIn("memory", self.text.lower())


class ReferenceDocTests(unittest.TestCase):
    def test_content_strategy_has_no_learnings_file_refs(self):
        cs = (SKILL / "references" / "content-strategy.md").read_text()
        self.assertNotIn("brand/learnings.md", cs)


class TemplateContractTests(unittest.TestCase):
    def setUp(self):
        self.html = (SKILL / "assets" / "for-you-template.html").read_text()

    def test_has_embed_placeholder(self):
        self.assertIn("/*__EMBEDDED_DATA__*/", self.html)

    def test_no_stale_external_data_script(self):
        # The old `<script src="feed-data.js">` handoff must be gone.
        self.assertNotIn('src="feed-data.js"', self.html)

    def test_renderer_reads_feed_data_global(self):
        self.assertIn("FEED_DATA", self.html)

    def test_feedback_layer_present(self):
        self.assertIn("__initFeedback", self.html)
        self.assertIn("FEEDBACK_MODE", self.html)

    def test_merged_posts_tab(self):
        # Posts + Ideas tabs, single posts list, sort/filter controls.
        self.assertIn('data-tab="posts"', self.html)
        self.assertIn('data-tab="ideas"', self.html)
        self.assertIn('id="posts-list"', self.html)
        self.assertIn("renderControlBar", self.html)
        self.assertIn("setupPostControls", self.html)
        self.assertIn('data-sort="popular"', self.html)
        self.assertIn('data-sort="recent"', self.html)
        self.assertIn("outlier-toggle", self.html)

    def test_old_three_tab_structure_gone(self):
        # The separate Competitors / Top Performers tabs were merged away.
        self.assertNotIn('data-tab="competitors"', self.html)
        self.assertNotIn('data-tab="top"', self.html)
        self.assertNotIn("renderCompetitors", self.html)
        self.assertNotIn("renderTopPerformers", self.html)


class CrossHostPackagingTests(unittest.TestCase):
    """Codex + Claude Code install from the same repo — the manifests and the
    skill-dir resolution must agree so the skill loads on both hosts."""

    def test_codex_manifest_points_at_skills_tree(self):
        manifest = _json(".codex-plugin/plugin.json")
        self.assertEqual("content-ideas", manifest["name"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertTrue((SKILL / "SKILL.md").is_file())
        self.assertTrue((SKILL / "scripts" / "scrape.py").is_file())

    def test_versions_match_across_manifests(self):
        version = _pyproject_version()
        self.assertEqual(version, _skill_version())
        self.assertEqual(version, _json(".codex-plugin/plugin.json")["version"])
        self.assertEqual(version, _json(".claude-plugin/plugin.json")["version"])

        plugins = _json(".claude-plugin/marketplace.json").get("plugins") or []
        self.assertEqual(1, len(plugins))
        self.assertEqual(version, plugins[0]["version"])

    def test_agents_md_delegates_to_claude_md(self):
        # Codex reads AGENTS.md; it should re-use the single CLAUDE.md guidance.
        self.assertEqual("@CLAUDE.md", (REPO / "AGENTS.md").read_text(encoding="utf-8").strip())
        self.assertTrue((REPO / "CLAUDE.md").is_file())

    def test_slash_command_present(self):
        self.assertTrue((REPO / "commands" / "content-ideas.md").is_file())

    def test_session_hook_present(self):
        hooks = _json("hooks/hooks.json")
        self.assertIn("SessionStart", hooks["hooks"])
        self.assertTrue((REPO / "hooks" / "scripts" / "check-setup.sh").is_file())

    def test_skill_resolves_for_codex_not_just_claude(self):
        # The resolution block must look beyond CLAUDE_PLUGIN_ROOT so Codex
        # (which never sets it) can still locate the scripts.
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(".codex/plugins/cache", text)
        self.assertIn(".claude/plugins/cache", text)


if __name__ == "__main__":
    unittest.main()
