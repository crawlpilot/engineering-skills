#!/usr/bin/env python3
"""Stand-in agent for testing the eval harness without model calls.

run_evals.py runs it in the eval workspace with EVAL_FIXTURE_DIR set. It behaves
like a good agent when the skill is installed (copies the fixture's strong
self-test suite and reports the boundary bug) and like a thin one without it
(copies the weak suite). It prints a minimal stream-json transcript, so the
whole pipeline, grading included, runs end to end in CI.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path


def emit(event: dict) -> None:
    print(json.dumps(event), flush=True)


def main() -> int:
    fixture = Path(os.environ["EVAL_FIXTURE_DIR"])
    skills = Path(".claude/skills")
    with_skill = skills.exists() and any(skills.iterdir())
    suite = "strong" if with_skill else "weak"
    shutil.copytree(fixture / "selftest" / suite, Path.cwd(), dirs_exist_ok=True)

    tool_uses = []
    if with_skill:
        name = next(skills.iterdir()).name
        tool_uses.append({"type": "tool_use", "name": "Skill", "input": {"skill": name}})
    tool_uses.append({"type": "tool_use", "name": "Bash", "input": {"command": "pytest -q"}})
    emit({"type": "assistant", "message": {"content": tool_uses}})

    report = ("Added tests. Found a boundary bug: 50 items returns STANDARD, but the docs say "
              "50 or more is BULK; the check should be >= 50.") if with_skill else "Added two tests."
    emit({"type": "result", "result": report, "is_error": False, "total_cost_usd": 0,
          "num_turns": 2, "duration_ms": 0})
    return 0


if __name__ == "__main__":
    sys.exit(main())
