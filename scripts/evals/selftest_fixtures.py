#!/usr/bin/env python3
"""Prove every eval fixture is fair before any model is graded on it.

For each fixture under evals/:
  1. The project as given builds and its existing tests pass.
  2. The known-good suite (selftest/strong) passes on the reference implementation,
     catches the planted bug and kills every mutant. A mutant it can't kill is
     either equivalent or a fixture bug, and fails the self-test.
  3. The known-weak suite (selftest/weak) scores clearly lower, so the grader
     separates good tests from thin ones.

Usage:
    python3 scripts/evals/selftest_fixtures.py               # every fixture
    python3 scripts/evals/selftest_fixtures.py --language python
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixtures import copy_tree, find_fixtures, grade, load_fixture, prepare, run  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
WEAK_MAX_SCORE = 60  # a typical-values-only suite must land well below a strong one


def overlay(fixture, suite: str) -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory(prefix=f"{fixture.id}-{suite}-")
    copy_tree(fixture.project, Path(tmp.name))
    copy_tree(fixture.root / "selftest" / suite, Path(tmp.name))
    return tmp


def check(fixture_dir: Path) -> list[str]:
    fixture = load_fixture(fixture_dir)
    problems: list[str] = []
    print(f"\n== {fixture.id}")

    try:
        fixture.variants()
    except ValueError as exc:
        return [str(exc)]

    ok, out = prepare(fixture)
    if not ok:
        return [f"prepare_command failed:\n{out}"]

    # Run in a copy so build output never lands inside the fixture.
    with tempfile.TemporaryDirectory(prefix=f"{fixture.id}-asis-") as tmp:
        copy_tree(fixture.project, Path(tmp))
        ok, out = run(fixture.command(fixture.test_command), Path(tmp))
    print(f"  project tests pass as given: {ok}")
    if not ok:
        problems.append(f"project's own tests fail:\n{out}")

    for suite in ("strong", "weak"):
        if not (fixture.root / "selftest" / suite).exists():
            problems.append(f"missing selftest/{suite}")
            continue
        with overlay(fixture, suite) as ws:
            g = grade(fixture, Path(ws))
        killed = sum(g.mutants_killed.values())
        print(f"  {suite:6} score {g.score:3}  reference pass {g.passes_on_reference}  "
              f"catches bug {g.catches_planted_bug}  mutants {killed}/{len(g.mutants_killed)}")
        if suite == "strong":
            if not g.passes_on_reference:
                problems.append("strong suite fails on the reference:\n" + g.outputs.get("reference", ""))
            if not g.catches_planted_bug:
                problems.append("strong suite does not catch the planted bug")
            survivors = [n for n, k in g.mutants_killed.items() if not k]
            if survivors:
                problems.append("strong suite leaves mutants alive (equivalent or broken?): "
                                + ", ".join(survivors))
        elif g.score > WEAK_MAX_SCORE:
            problems.append(f"weak suite scores {g.score} > {WEAK_MAX_SCORE}: mutants are too easy")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--language", help="only fixtures for this language")
    parser.add_argument("--root", type=Path, default=ROOT / "evals")
    args = parser.parse_args()

    dirs = find_fixtures(args.root)
    if args.language:
        dirs = [d for d in dirs if load_fixture(d).language == args.language]
    if not dirs:
        print("no fixtures found")
        return 1

    failed = 0
    for d in dirs:
        problems = check(d)
        for p in problems:
            print(f"  FAIL {p}")
        failed += bool(problems)
    print(f"\n{len(dirs) - failed}/{len(dirs)} fixtures pass their self-test.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
