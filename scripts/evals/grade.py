#!/usr/bin/env python3
"""Grade one workspace against one fixture, without running an agent.

Useful for checking a fixture by hand, or grading work done elsewhere.

Usage:
    python3 scripts/evals/grade.py evals/unit-testing/fixtures/tier-boundary/java path/to/workspace
    python3 scripts/evals/grade.py FIXTURE WORKSPACE --report report.txt --verbose
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixtures import grade_any, load_fixture, prepare  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("fixture", type=Path)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--report", type=Path, help="file holding the agent's final report")
    parser.add_argument("--commands", type=Path, help="file with the shell commands the agent ran, one per line")
    parser.add_argument("--verbose", action="store_true", help="include test output per variant")
    args = parser.parse_args()

    fixture = load_fixture(args.fixture.resolve())
    ok, out = prepare(fixture)
    if not ok:
        sys.exit(f"prepare_command failed:\n{out}")
    report = args.report.read_text(encoding="utf-8") if args.report else None
    commands = args.commands.read_text().splitlines() if args.commands else None
    g = grade_any(fixture, args.workspace.resolve(), report=report, commands=commands)
    print(json.dumps(g.to_dict(with_outputs=args.verbose), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
