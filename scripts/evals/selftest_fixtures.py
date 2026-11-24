#!/usr/bin/env python3
"""Prove every eval fixture is fair before any model is graded on it.

For each fixture under evals/:
  1. The starting workspace (project/, plus change/ if any) builds and its tests pass.
  2. The known-good answer (selftest/strong) scores 100. For a mutation fixture that
     also means it passes on the reference, catches the planted bug and kills every
     mutant; a mutant it can't kill is equivalent or broken.
  3. Every mutant (and the planted bug) builds and passes the project's existing
     tests. A mutant that doesn't compile would be "killed" by any suite, and one
     the existing tests already catch proves nothing about the agent's tests.
  4. The known-weak answer (selftest/weak) scores at most 60, and so does doing
     nothing at all, so the grader separates good work from thin work.

A selftest answer is a directory overlaid on the starting workspace. Two files in
it are not copied: REPORT.md is used as the agent's final report, and COMMANDS.txt
(one shell command per line) as the commands it ran.

Usage:
    python3 scripts/evals/selftest_fixtures.py                    # every fixture
    python3 scripts/evals/selftest_fixtures.py --language python
    python3 scripts/evals/selftest_fixtures.py --strict           # fail, don't skip, on missing docker
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checks import starting_workspace  # noqa: E402
from fixtures import (copy_tree, find_fixtures, grade_any, load_fixture,  # noqa: E402
                      missing_requirements, prepare, run)

ROOT = Path(__file__).resolve().parents[2]
WEAK_MAX_SCORE = 60  # a thin answer must land well below a strong one
ANSWER_META = ("REPORT.md", "COMMANDS.txt")


def apply_answer(answer: Path, workspace: Path) -> tuple[str | None, list[str] | None]:
    """Overlay an answer directory; return its report and commands, if given."""
    copy_tree(answer, workspace)
    report = commands = None
    for name in ANSWER_META:
        if (workspace / name).exists():
            (workspace / name).unlink()
    if (answer / "REPORT.md").exists():
        report = (answer / "REPORT.md").read_text(encoding="utf-8")
    if (answer / "COMMANDS.txt").exists():
        commands = [c for c in (answer / "COMMANDS.txt").read_text().splitlines() if c.strip()]
    return report, commands


def check(fixture_dir: Path, strict: bool) -> tuple[list[str], bool]:
    """Return (problems, skipped)."""
    fixture = load_fixture(fixture_dir)
    print(f"\n== {fixture.id} ({fixture.kind})")
    missing = missing_requirements(fixture)
    if missing:
        msg = f"needs {', '.join(missing)}"
        print(f"  SKIP {msg}")
        return ([msg] if strict else []), not strict

    if fixture.kind == "mutation":
        try:
            fixture.variants()
        except ValueError as exc:
            return [str(exc)], False

    ok, out = prepare(fixture)
    if not ok:
        return [f"prepare_command failed:\n{out}"], False

    problems: list[str] = []
    with tempfile.TemporaryDirectory(prefix=f"{fixture.id}-asis-") as tmp:
        starting_workspace(fixture, Path(tmp))
        ok, out = run(fixture.command(fixture.test_command), Path(tmp))
    print(f"  starting workspace tests pass: {ok}")
    if not ok:
        problems.append(f"starting workspace tests fail:\n{out}")

    for name, problem in mutant_problems(fixture):
        problems.append(f"{name}: {problem}")

    with tempfile.TemporaryDirectory(prefix=f"{fixture.id}-noop-") as tmp:
        starting_workspace(fixture, Path(tmp))
        g = grade_any(fixture, Path(tmp), report="", commands=[])
    print(f"  noop   score {g.score:3}")
    if g.score > WEAK_MAX_SCORE:
        problems.append(f"doing nothing scores {g.score} > {WEAK_MAX_SCORE}")

    for suite in ("strong", "weak"):
        answer = fixture.root / "selftest" / suite
        if not answer.exists():
            problems.append(f"missing selftest/{suite}")
            continue
        with tempfile.TemporaryDirectory(prefix=f"{fixture.id}-{suite}-") as tmp:
            ws = Path(tmp)
            starting_workspace(fixture, ws)
            report, commands = apply_answer(answer, ws)
            g = grade_any(fixture, ws, report=report, commands=commands)
        print(f"  {suite:6} score {g.score:3}  {summary(g)}")
        if suite == "strong" and g.score != 100:
            problems.append(f"strong answer scores {g.score}, not 100: {details(g)}")
        if suite == "weak" and g.score > WEAK_MAX_SCORE:
            problems.append(f"weak answer scores {g.score} > {WEAK_MAX_SCORE}: checks are too easy")
    return problems, False


def mutant_problems(fixture) -> list[tuple[str, str]]:
    """Each mutant must build and pass the starting workspace's own tests."""
    from checks import _run_in_copy
    edits: dict[str, list[dict]] = {}
    if fixture.kind == "mutation":
        for name, text in fixture.variants().items():
            if name != "reference":
                edits[name] = [{"file": fixture.implementation, "whole": text}]
    for c in fixture.checks:
        if c["type"] == "mutation":
            for m in c["mutants"]:
                edits[f"mutant:{m['name']}"] = [{"file": m.get("file", c.get("file")),
                                                 "find": m["find"], "replace": m["replace"]}]
    if not edits:
        return []
    out = []
    with tempfile.TemporaryDirectory(prefix=f"{fixture.id}-mutants-") as tmp:
        start = Path(tmp)
        starting_workspace(fixture, start)
        for name, e in edits.items():
            if "whole" in e[0]:
                e = [{"file": e[0]["file"], "find": (start / e[0]["file"]).read_text(encoding="utf-8"),
                      "replace": e[0]["whole"]}]
            ok, out_text = _run_in_copy(fixture, start, None, e, fixture.test_command)
            if ok is None:
                out.append((name, f"could not apply: {out_text}"))
            elif not ok:
                out.append((name, "fails to build, or the existing tests already catch it:\n"
                                  + out_text[-1500:]))
    print(f"  mutants build and survive existing tests: {len(edits) - len(out)}/{len(edits)}")
    return out


def summary(g) -> str:
    if hasattr(g, "mutants_killed"):
        killed = sum(g.mutants_killed.values())
        return (f"reference pass {g.passes_on_reference}  catches bug {g.catches_planted_bug}  "
                f"mutants {killed}/{len(g.mutants_killed)}")
    return "  ".join(f"{r.name}:{'skip' if r.passed is None else ('ok' if r.passed else 'FAIL')}"
                     for r in g.checks)


def details(g) -> str:
    if hasattr(g, "checks"):
        return "; ".join(f"{r.name}: {r.note}" for r in g.checks if not r.passed) or "; ".join(g.notes)
    return "; ".join(g.notes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--language", help="only fixtures for this language")
    parser.add_argument("--skill", help="only fixtures for this skill")
    parser.add_argument("--strict", action="store_true", help="treat missing requirements as failures")
    parser.add_argument("--root", type=Path, default=ROOT / "evals")
    args = parser.parse_args()

    dirs = find_fixtures(args.root)
    if args.skill:
        dirs = [d for d in dirs if d.relative_to(args.root).parts[0] == args.skill]
    if args.language:
        dirs = [d for d in dirs if load_fixture(d).language == args.language]
    if not dirs:
        print("no fixtures found")
        return 1
    if not shutil.which("git"):
        print("git is required")
        return 1

    failed = skipped = 0
    for d in dirs:
        problems, was_skipped = check(d, args.strict)
        for p in problems:
            print(f"  FAIL {p}")
        failed += bool(problems)
        skipped += was_skipped
    passed = len(dirs) - failed - skipped
    print(f"\n{passed}/{len(dirs)} fixtures pass their self-test"
          + (f", {skipped} skipped" if skipped else "") + ".")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
