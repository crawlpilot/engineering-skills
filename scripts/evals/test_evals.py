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
import checks  # noqa: E402
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

    def test_braces_match_any_option(self):
        rx = fixtures.glob_to_regex("{src,tests}/**")
        self.assertTrue(rx.match("src/a/b.py"))
        self.assertTrue(rx.match("tests/t.py"))
        self.assertFalse(rx.match("docs/x.md"))

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
    def test_every_fixture_is_well_formed(self):
        """Static checks on every fixture.yaml; nothing is built or run."""
        known = {"run", "grep", "unchanged", "report", "ran", "uv_lock", "mutation"}
        dirs = fixtures.find_fixtures(ROOT / "evals")
        self.assertTrue(dirs, "no fixtures found")
        for d in dirs:
            f = fixtures.load_fixture(d)
            with self.subTest(fixture=f.id):
                self.assertTrue((d / "selftest" / "strong").is_dir())
                self.assertTrue((d / "selftest" / "weak").is_dir())
                if f.kind == "mutation":
                    variants = f.variants()  # raises if a find string is missing or repeated
                    self.assertEqual(len(set(variants.values())), len(variants))
                    continue
                with tempfile.TemporaryDirectory() as tmp:
                    start = Path(tmp)
                    checks.starting_workspace(f, start)
                    names = [c["name"] for c in f.checks]
                    self.assertEqual(len(names), len(set(names)), "duplicate check names")
                    self.assertGreater(sum(int(c.get("points", 0)) for c in f.checks), 0)
                    for c in f.checks:
                        self.assertIn(c["type"], known, c["name"])
                        if c.get("only_if"):
                            self.assertIn(c["only_if"], names, c["name"])
                        if c.get("overlay"):
                            self.assertTrue((d / c["overlay"]).is_dir(), c["overlay"])
                        for e in c.get("edits", []):
                            self.assertIsNone(checks._apply_edits(start, []))
                            self.assertTrue((start / e["file"]).exists(), e["file"])
                        for m in c.get("mutants", []):
                            text = (start / m.get("file", c.get("file", ""))).read_text()
                            self.assertEqual(text.count(m["find"]), 1, f"mutant {m['name']}")

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


class ChecksTest(unittest.TestCase):
    """Check types on a tiny in-memory fixture; nothing is built or run."""

    def make(self, checks_list):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "project").mkdir()
        (root / "project" / "app.txt").write_text("hello\n")
        f = fixtures.Fixture(root=root, id="t", language="python", test_command="true",
                             checks=checks_list)
        ws = root / "ws"
        fixtures.copy_tree(f.project, ws)
        return f, ws

    def test_report_patterns_and_absent(self):
        f, ws = self.make([{"name": "r", "type": "report", "points": 10,
                            "patterns": ["bug"], "absent": ["(?i)lgtm"]}])
        self.assertEqual(checks.grade_checks(f, ws, report="found a bug").score, 100)
        self.assertEqual(checks.grade_checks(f, ws, report="bug, but LGTM").score, 0)

    def test_skipped_checks_do_not_count(self):
        f, ws = self.make([{"name": "r", "type": "report", "points": 50, "patterns": ["x"]},
                           {"name": "u", "type": "unchanged", "files": "*.txt", "points": 50}])
        g = checks.grade_checks(f, ws, report=None)
        self.assertIsNone(g.checks[0].passed)
        self.assertEqual(g.score, 100)

    def test_unchanged_sees_edits_and_new_files(self):
        f, ws = self.make([{"name": "u", "type": "unchanged", "files": "*.txt", "points": 10}])
        (ws / "new.txt").write_text("x")
        self.assertIn("new.txt", checks.grade_checks(f, ws).checks[0].note)

    def test_only_if_withholds_points_but_not_the_gate(self):
        f, ws = self.make([
            {"name": "fix", "type": "report", "points": 50, "patterns": ["fixed"]},
            {"name": "restraint", "type": "unchanged", "files": "*.txt", "points": 50,
             "gate": True, "only_if": "fix"}])
        g = checks.grade_checks(f, ws, report="nothing done")
        self.assertEqual(g.score, 0)
        self.assertTrue(g.checks[1].passed)  # passed, so the gate holds
        self.assertEqual(g.checks[1].earned, 0)
        self.assertEqual(checks.grade_checks(f, ws, report="fixed").score, 100)

    def test_gate_failure_zeroes_the_score(self):
        f, ws = self.make([{"name": "g", "type": "report", "points": 10, "gate": True,
                            "patterns": ["yes"]},
                           {"name": "u", "type": "unchanged", "files": "*.txt", "points": 90}])
        self.assertEqual(checks.grade_checks(f, ws, report="no").score, 0)

    def test_regex_edit_reports_missing_target(self):
        f, ws = self.make([])
        err = checks._apply_edits(ws, [{"file": "app.txt", "find": "^bye", "replace": "x",
                                        "regex": True}])
        self.assertIn("not found", err)

    def test_version_compare(self):
        self.assertLess(checks._version("2.2.1"), checks._version("2.5.0"))
        self.assertGreater(checks._version("2.10.0"), checks._version("2.5.0"))


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
