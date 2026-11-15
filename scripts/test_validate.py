#!/usr/bin/env python3
"""Tests for validate.py. Run: python3 scripts/test_validate.py"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402

GOOD_DESCRIPTION = (
    "Write tests for a thing. Use when asked to add tests or when changed logic has none. "
    "Not for tests needing a real database."
)
GOOD_BODY = "# Demo\n\n## Workflow\n\n1. Step.\n\n## Do not\n\n- Thing.\n\n## Report\n\nSay what happened.\n"


def make_skill(root: Path, name: str = "demo", description: str = GOOD_DESCRIPTION,
               body: str = GOOD_BODY, front_name: str | None = None,
               sources: bool = True, evals: bool = True) -> Path:
    skill = root / "skills" / name
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {front_name or name}\ndescription: {description}\n---\n\n{body}", encoding="utf-8")
    if sources:
        (skill / "references" / "sources.md").write_text("# Sources\n", encoding="utf-8")
    if evals:
        (root / "evals" / name).mkdir(parents=True)
        (root / "evals" / name / "cases.md").write_text("# Cases\n", encoding="utf-8")
    return skill


class ValidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def errors(self) -> list[str]:
        return validate.check_repo(self.root)

    def test_valid_skill_has_no_errors(self) -> None:
        make_skill(self.root)
        self.assertEqual(self.errors(), [])

    def test_empty_repo_is_an_error(self) -> None:
        self.assertTrue(any("no skill folders" in e for e in self.errors()))

    def test_missing_front_matter(self) -> None:
        skill = make_skill(self.root)
        (skill / "SKILL.md").write_text(GOOD_BODY, encoding="utf-8")
        self.assertTrue(any("missing front matter" in e for e in self.errors()))

    def test_name_must_match_folder(self) -> None:
        make_skill(self.root, front_name="other")
        self.assertTrue(any("does not match folder" in e for e in self.errors()))

    def test_description_must_say_when_to_use(self) -> None:
        make_skill(self.root, description="Writes tests for things in a codebase, covering many cases and "
                                          "frameworks across several languages.")
        self.assertTrue(any("does not say when to use" in e for e in self.errors()))

    def test_description_too_short(self) -> None:
        make_skill(self.root, description="Use when testing.")
        self.assertTrue(any("characters" in e for e in self.errors()))

    def test_missing_required_section(self) -> None:
        make_skill(self.root, body="# Demo\n\n## Workflow\n\n1. Step.\n\n## Report\n\nDone.\n")
        self.assertTrue(any("missing section '## Do not'" in e for e in self.errors()))

    def test_core_over_line_limit(self) -> None:
        make_skill(self.root, body=GOOD_BODY + "line\n" * 250)
        self.assertTrue(any("limit 200" in e for e in self.errors()))

    def test_broken_relative_link(self) -> None:
        make_skill(self.root, body=GOOD_BODY + "\nSee [java](references/java.md).\n")
        self.assertTrue(any("broken link -> references/java.md" in e for e in self.errors()))

    def test_working_relative_link_and_urls_pass(self) -> None:
        skill = make_skill(self.root, body=GOOD_BODY + "\nSee [java](references/java.md) and "
                                                       "[site](https://example.com) and [top](#demo).\n")
        (skill / "references" / "java.md").write_text("# Java\n", encoding="utf-8")
        self.assertEqual(self.errors(), [])

    def test_links_inside_code_fences_are_ignored(self) -> None:
        make_skill(self.root, body=GOOD_BODY + "\n```text\n[x](missing.md)\n```\n")
        self.assertEqual(self.errors(), [])

    def test_missing_sources_and_evals(self) -> None:
        make_skill(self.root, sources=False, evals=False)
        errs = self.errors()
        self.assertTrue(any("sources.md is missing" in e for e in errs))
        self.assertTrue(any("cases.md is missing" in e for e in errs))

    def test_invalid_manifest_json(self) -> None:
        make_skill(self.root)
        (self.root / ".claude-plugin").mkdir()
        (self.root / ".claude-plugin" / "plugin.json").write_text("{not json", encoding="utf-8")
        self.assertTrue(any("invalid JSON" in e for e in self.errors()))


if __name__ == "__main__":
    unittest.main()
