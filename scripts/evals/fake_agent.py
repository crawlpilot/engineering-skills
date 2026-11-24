#!/usr/bin/env python3
"""Stand-in agent for testing the eval harness without model calls.

run_evals.py runs it in the eval workspace with EVAL_FIXTURE_DIR set. With the
skill installed it gives the fixture's known-good answer (selftest/strong);
without it, the known-weak one (selftest/weak). An answer's REPORT.md becomes the
final report and COMMANDS.txt the shell commands it "ran". It prints a minimal
stream-json transcript, so the whole pipeline, grading included, runs end to end.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

META = ("REPORT.md", "COMMANDS.txt")


def emit(event: dict) -> None:
    print(json.dumps(event), flush=True)


def main() -> int:
    fixture = Path(os.environ["EVAL_FIXTURE_DIR"])
    skills = Path(".claude/skills")
    with_skill = skills.exists() and any(skills.iterdir())
    answer = fixture / "selftest" / ("strong" if with_skill else "weak")
    shutil.copytree(answer, Path.cwd(), dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(*META))

    report = (answer / "REPORT.md").read_text() if (answer / "REPORT.md").exists() else (
        "Added tests. Found a boundary bug: 50 items returns STANDARD, but the docs say "
        "50 or more is BULK; the check should be >= 50." if with_skill else "Added two tests.")
    commands = ((answer / "COMMANDS.txt").read_text().splitlines()
                if (answer / "COMMANDS.txt").exists() else ["pytest -q"])

    tool_uses = []
    if with_skill:
        tool_uses.append({"type": "tool_use", "name": "Skill",
                          "input": {"skill": next(skills.iterdir()).name}})
    tool_uses += [{"type": "tool_use", "name": "Bash", "input": {"command": c}}
                  for c in commands if c.strip()]
    emit({"type": "assistant", "message": {"content": tool_uses}})
    emit({"type": "result", "result": report, "is_error": False, "total_cost_usd": 0,
          "num_turns": 2, "duration_ms": 0})
    return 0


if __name__ == "__main__":
    sys.exit(main())
