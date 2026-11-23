#!/usr/bin/env python3
"""Fast tests for the eval harness. No builds, no model calls.

Run: python3 scripts/evals/test_evals.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixtures  # noqa: E402
import run_routing  # noqa: E402
import transcript  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


class GlobTest(unittest.TestCase):
    def test_double_star_matches_zero_or_more_directories(self):
        rx = fixtures.glob_to_regex("tests/**/*.py")
        self.assertTrue(rx.match("tests/test_a.py"))
        self.assertTrue(rx.match("tests/unit/deep/test_a.py"))
        self.assertFalse(rx.match("src/a.py"))
        self.assertFalse(rx.match("tests/test_a.pyc"))

    def test_single_star_stays_inside_one_directory(self):
        rx = fixtures.glob_to_regex("src/*.java")
        self.assertTrue(rx.match("src/A.java"))
        self.assertFalse(rx.match("src/a/A.java"))


class ReplacementTest(unittest.TestCase):
    def test_applies_exactly_one_match(self):
        r = fixtures.Replacement(find="a > b", replace="a >= b")
        self.assertEqual(r.apply("if a > b:", "t"), "if a >= b:")

    def test_rejects_missing_or_repeated_match(self):
        r = fixtures.Replacement(find="x", replace="y")
        with self.assertRaisesRegex(ValueError, "found 0"):
            r.apply("abc", "t")
        with self.assertRaisesRegex(ValueError, "found 2"):
            r.apply("x x", "t")


class FixtureFilesTest(unittest.TestCase):
    def test_every_fixture_has_valid_variants(self):
        dirs = fixtures.find_fixtures(ROOT / "evals")
        self.assertTrue(dirs, "no fixtures found")
        for d in dirs:
            f = fixtures.load_fixture(d)
            variants = f.variants()  # raises if a find string is missing or repeated
            self.assertEqual(len(set(variants.values())), len(variants),
                             f"{f.id}: two variants are identical")

    def test_detects_added_and_changed_tests_only(self):
        f = fixtures.load_fixture(ROOT / "evals/unit-testing/fixtures/tier-boundary/python")
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            fixtures.copy_tree(f.project, ws)
            self.assertEqual(fixtures.test_files(f, ws), {})
            (ws / "tests/test_new.py").write_text("def test_x(): pass\n")
            (ws / "tests/test_money.py").write_text("# changed\n")
            (ws / "src/pricing/extra.py").write_text("X = 1\n")
            self.assertEqual(fixtures.test_files(f, ws),
                             {"tests/test_new.py": "added", "tests/test_money.py": "changed"})

    def test_no_tests_scores_zero(self):
        f = fixtures.load_fixture(ROOT / "evals/unit-testing/fixtures/tier-boundary/python")
        with tempfile.TemporaryDirectory() as tmp:
            fixtures.copy_tree(f.project, Path(tmp))
            g = fixtures.grade(f, Path(tmp))
        self.assertEqual(g.score, 0)
        self.assertIn("no test files", g.notes[0])


class TranscriptTest(unittest.TestCase):
    def lines(self, *events):
        return "\n".join(json.dumps(e) for e in events)

    def test_reads_tools_result_and_skills(self):
        raw = self.lines(
            {"type": "system", "subtype": "init"},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": "unit-testing"}},
                {"type": "tool_use", "name": "Read",
                 "input": {"file_path": "/w/.claude/skills/unit-testing/references/java.md"}},
                {"type": "tool_use", "name": "Bash", "input": {"command": "mvn -q test"}}]}},
            {"type": "result", "result": "done", "total_cost_usd": 0.12, "num_turns": 4},
        )
        t = transcript.parse(raw)
        self.assertEqual(t.result, "done")
        self.assertEqual(t.bash_commands, ["mvn -q test"])
        self.assertEqual(t.skills_used(), {"unit-testing"})
        self.assertEqual(t.references_read(), ["unit-testing/references/java.md"])
        self.assertAlmostEqual(t.cost_usd, 0.12)

    def test_reading_skill_md_counts_as_using_the_skill(self):
        raw = self.lines({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Read",
             "input": {"file_path": "/w/.claude/skills/code-review/SKILL.md"}}]}})
        self.assertEqual(transcript.parse(raw).skills_used(), {"code-review"})

    def test_ignores_non_json_noise(self):
        self.assertEqual(transcript.parse("warning: something\n{bad json").tool_uses, [])


class RoutingCasesTest(unittest.TestCase):
    def test_parses_every_skill_with_both_directions(self):
        skills = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())
        cases = run_routing.parse_cases(skills)
        for skill in skills:
            mine = [c for c in cases if c.skill == skill]
            self.assertTrue(any(c.should_invoke for c in mine), f"{skill}: no positive prompts")
            self.assertTrue(any(not c.should_invoke for c in mine), f"{skill}: no negative prompts")

    def test_hints_only_name_real_skills(self):
        skills = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())
        for c in run_routing.parse_cases(skills):
            self.assertTrue(set(c.hint) <= set(skills))


if __name__ == "__main__":
    unittest.main(verbosity=1)
