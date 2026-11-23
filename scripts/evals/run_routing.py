#!/usr/bin/env python3
"""Check that each prompt in evals/*/cases.md routes to the right skill.

All skills are installed into one workspace, so they compete for each prompt the
way they would for a user. For each trigger prompt the agent runs until it either
invokes a skill or makes a few tool calls without one, and is then stopped. Only
the routing decision is measured, not the work.

Prompts come from the "## Trigger" section of each cases.md:
  - "Should invoke" prompts pass if that skill is invoked.
  - "Should not invoke" prompts pass if that skill is not invoked. A hint in
    brackets naming other skills, "(unit-testing)" or "(design-patterns or
    coding-standards)", is reported as the expected destination but not required.

Usage:
    ANTHROPIC_API_KEY=... python3 scripts/evals/run_routing.py --model sonnet
    python3 scripts/evals/run_routing.py --list      # show parsed prompts, no calls
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transcript import parse as parse_transcript  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ITEM_RE = re.compile(r'^\d+\.\s+"(?P<prompt>.+?)"\s*(?:\((?P<hint>[^)]*)\))?\s*$')
# Stop a run after this many tool calls with no skill: routing has happened by then.
MAX_TOOL_CALLS_WITHOUT_SKILL = 3
ROUTING_TIMEOUT_SECONDS = 180


@dataclass
class TriggerCase:
    skill: str
    prompt: str
    should_invoke: bool
    hint: list[str]


def parse_cases(skills: list[str]) -> list[TriggerCase]:
    cases: list[TriggerCase] = []
    for skill in skills:
        text = (ROOT / "evals" / skill / "cases.md").read_text(encoding="utf-8")
        section = text.split("## Trigger", 1)[-1].split("\n## ", 1)[0]
        mode = None
        for line in section.splitlines():
            if line.startswith("Should invoke"):
                mode = True
            elif line.startswith("Should not invoke"):
                mode = False
            elif mode is not None and (m := ITEM_RE.match(line.strip())):
                hint = [h.strip() for h in re.split(r"\bor\b|,", m.group("hint") or "")]
                cases.append(TriggerCase(skill, m.group("prompt").replace("`", ""), mode,
                                         [h for h in hint if h in skills]))
    return cases


def route(prompt: str, workspace: Path, model: str) -> tuple[set[str], str]:
    """Run until the first skill call (or a few tool calls); return skills used + raw."""
    with tempfile.TemporaryDirectory(prefix="claude-config-") as config_dir:
        env = dict(os.environ, CLAUDE_CONFIG_DIR=config_dir)
        cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "stream-json",
               "--verbose", "--setting-sources", "project", "--no-session-persistence",
               "--allowed-tools", "Read Glob Grep Skill", "--max-budget-usd", "0.50"]
        proc = subprocess.Popen(cmd, cwd=workspace, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, text=True)
        lines: list[str] = []
        deadline = time.monotonic() + ROUTING_TIMEOUT_SECONDS
        assert proc.stdout is not None
        for line in proc.stdout:
            lines.append(line)
            t = parse_transcript("".join(lines))
            if t.skills_used() or len(t.tool_uses) >= MAX_TOOL_CALLS_WITHOUT_SKILL \
                    or time.monotonic() > deadline:
                break
        proc.kill()
        proc.wait()
    raw = "".join(lines)
    return parse_transcript(raw).skills_used(), raw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--list", action="store_true", help="print parsed cases and exit")
    parser.add_argument("--out", type=Path, default=ROOT / "evals" / "results" / ("routing-" + time.strftime("%Y%m%d-%H%M%S")))
    args = parser.parse_args()

    skills = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())
    cases = parse_cases(skills)
    if args.list:
        for c in cases:
            arrow = "->" if c.should_invoke else "!>"
            hint = f"  (expect {' or '.join(c.hint)})" if c.hint else ""
            print(f"{c.skill:20} {arrow} {c.prompt}{hint}")
        print(f"\n{len(cases)} cases across {len(skills)} skills")
        return 0
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set")

    args.out.mkdir(parents=True, exist_ok=True)
    passed = 0
    rows = []
    with tempfile.TemporaryDirectory(prefix="routing-") as tmp:
        ws = Path(tmp)
        for skill in skills:
            shutil.copytree(ROOT / "skills" / skill, ws / ".claude" / "skills" / skill)
        subprocess.run(["git", "init", "-q"], cwd=ws, check=True)
        for c in cases:
            used, raw = route(c.prompt, ws, args.model)
            ok = (c.skill in used) if c.should_invoke else (c.skill not in used)
            passed += ok
            rows.append({"skill": c.skill, "prompt": c.prompt, "should_invoke": c.should_invoke,
                         "used": sorted(used), "hint": c.hint, "pass": ok})
            print(f"{'PASS' if ok else 'FAIL'} {c.skill:20} {'->' if c.should_invoke else '!>'} "
                  f"{c.prompt}  [used: {', '.join(sorted(used)) or 'none'}]", flush=True)
    rate = passed / len(cases)
    (args.out / "routing.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    print(f"\nRouting: {passed}/{len(cases)} ({rate:.0%}) on {args.model}")
    return 0 if rate >= 0.9 else 1


if __name__ == "__main__":
    sys.exit(main())
