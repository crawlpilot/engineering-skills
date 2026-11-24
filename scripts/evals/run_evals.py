#!/usr/bin/env python3
"""Run a skill's eval tasks with and without the skill, and grade the results.

For each task in evals/<skill>/cases.yaml, each fixture, each model and each mode:
  1. Copy the fixture's project into a fresh git repository.
  2. In "with" mode, install skills/<skill> into the workspace's .claude/skills/.
  3. Run Claude Code headless on the task prompt, with user settings and user
     skills isolated, and save the stream-json transcript.
  4. Grade the workspace with the fixture's reference and mutants
     (scripts/evals/fixtures.py), plus process checks on the transcript.

Results go to <out>/results.jsonl and <out>/summary.md, and the summary is printed.

Usage:
    ANTHROPIC_API_KEY=... python3 scripts/evals/run_evals.py --skill unit-testing \\
        --models haiku,sonnet,opus --repeat 3

    # Plumbing check with no model calls (CI uses this):
    python3 scripts/evals/run_evals.py --skill unit-testing --language python \\
        --agent-cmd "python3 scripts/evals/fake_agent.py"

Each "with" run costs one agent session per fixture per model per repeat; use
--max-budget-usd to cap each session.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checks import git_with_change  # noqa: E402
from fixtures import copy_tree, grade_any, load_fixture, missing_requirements, prepare  # noqa: E402
from transcript import parse as parse_transcript  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_TOOLS = "Bash Read Edit Write Glob Grep Skill TodoWrite"
AGENT_TIMEOUT_SECONDS = 1800  # a JVM agent run that compiles and tests several times


def run_agent(workspace: Path, prompt: str, model: str, args, fixture_dir: Path) -> str:
    """Run the agent in `workspace` and return its stream-json transcript."""
    with tempfile.TemporaryDirectory(prefix="claude-config-") as config_dir:
        env = dict(os.environ)
        # A fresh config dir keeps the user's own skills, memory and settings out.
        env["CLAUDE_CONFIG_DIR"] = config_dir
        env["EVAL_FIXTURE_DIR"] = str(fixture_dir)
        if args.agent_cmd:
            cmd = shlex.split(args.agent_cmd) + [prompt]
        else:
            cmd = ["claude", "-p", prompt, "--model", model,
                   "--output-format", "stream-json", "--verbose",
                   "--setting-sources", "project",
                   "--allowed-tools", ALLOWED_TOOLS,
                   "--no-session-persistence"]
            if args.max_budget_usd:
                cmd += ["--max-budget-usd", str(args.max_budget_usd)]
        try:
            proc = subprocess.run(cmd, cwd=workspace, env=env, capture_output=True,
                                  text=True, timeout=AGENT_TIMEOUT_SECONDS)
            return proc.stdout + ("\n" + proc.stderr if proc.returncode else "")
        except subprocess.TimeoutExpired as exc:
            return (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")


def run_one(task: dict, fixture_dir: Path, skill: str, model: str, mode: str,
            attempt: int, args, out_dir: Path) -> dict:
    fixture = load_fixture(fixture_dir)
    label = f"{task['id']}/{fixture.language}/{model}/{mode}/{attempt}"
    print(f"  running {label}", flush=True)
    with tempfile.TemporaryDirectory(prefix=f"eval-{fixture.id}-") as tmp:
        ws = Path(tmp)
        copy_tree(fixture.project, ws)
        git_with_change(fixture, ws)  # project on main; change/ on a feature branch
        if mode == "with":
            # Installed after the commits, so the skill never shows up in the diff.
            shutil.copytree(ROOT / "skills" / skill, ws / ".claude" / "skills" / skill)
            (ws / ".git" / "info" / "exclude").write_text(".claude/\n")

        started = time.monotonic()
        raw = run_agent(ws, task["prompt"], model, args, fixture_dir)
        elapsed = time.monotonic() - started
        transcript_path = out_dir / "transcripts" / (label.replace("/", "__") + ".jsonl")
        transcript_path.parent.mkdir(parents=True, exist_ok=True)
        transcript_path.write_text(raw, encoding="utf-8")
        t = parse_transcript(raw)

        g = grade_any(fixture, ws, report=t.result or None, commands=t.bash_commands)
        process = {name: any(re.search(pattern, c) for c in t.bash_commands)
                   for name, pattern in (task.get("process") or {}).items()}

    return {
        "task": task["id"], "fixture": fixture.id, "language": fixture.language,
        "model": model, "mode": mode, "attempt": attempt,
        "score": g.score, "grade": g.to_dict(), "process": process,
        "skill_loaded": skill in t.skills_used(),
        "references_read": t.references_read(),
        "agent_error": t.is_error or not t.result,
        "cost_usd": t.cost_usd, "turns": t.turns, "seconds": round(elapsed, 1),
        "transcript": str(transcript_path.relative_to(out_dir)),
    }


def summarize(records: list[dict]) -> str:
    groups: dict[tuple, dict[str, list[dict]]] = {}
    for r in records:
        groups.setdefault((r["task"], r["language"], r["model"]), {}).setdefault(r["mode"], []).append(r)

    def mean(rs, key):
        return statistics.mean(r[key] for r in rs) if rs else None

    lines = ["| Task | Language | Model | Without | With | Delta | Skill loaded | Ran tests | Cost with ($) |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for (task, lang, model), modes in sorted(groups.items()):
        without, with_ = modes.get("without", []), modes.get("with", [])
        a, b = mean(without, "score"), mean(with_, "score")
        delta = f"{b - a:+.0f}" if a is not None and b is not None else "n/a"
        loaded = (f"{sum(r['skill_loaded'] for r in with_)}/{len(with_)}" if with_ else "n/a")
        rows = with_ or without
        ran = (f"{sum(r['process'].get('ran_tests', False) for r in rows)}/{len(rows)}"
               if any("ran_tests" in r["process"] for r in rows) else "in score")
        cost = mean(with_, "cost_usd")
        lines.append(f"| {task} | {lang} | {model} | "
                     f"{'n/a' if a is None else f'{a:.0f}'} | {'n/a' if b is None else f'{b:.0f}'} | "
                     f"{delta} | {loaded} | {ran} | "
                     f"{'n/a' if cost is None else f'{cost:.2f}'} |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skill", required=True)
    parser.add_argument("--models", default="sonnet", help="comma-separated, e.g. haiku,sonnet,opus")
    parser.add_argument("--modes", default="without,with")
    parser.add_argument("--language", help="only fixtures for this language")
    parser.add_argument("--task", help="only this task id")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--max-budget-usd", type=float, default=2.0, help="cap per agent session")
    parser.add_argument("--agent-cmd", help="run this instead of claude (prompt is appended); for plumbing tests")
    parser.add_argument("--out", type=Path, default=ROOT / "evals" / "results" / time.strftime("%Y%m%d-%H%M%S"))
    args = parser.parse_args()

    if not args.agent_cmd and not shutil.which("claude"):
        sys.exit("claude CLI not found: npm install -g @anthropic-ai/claude-code")
    if not args.agent_cmd and not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set")

    cases = yaml.safe_load((ROOT / "evals" / args.skill / "cases.yaml").read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    prepared: set[Path] = set()
    for task in cases["tasks"]:
        if args.task and task["id"] != args.task:
            continue
        for rel in task["fixtures"]:
            fixture_dir = ROOT / "evals" / args.skill / rel
            fixture = load_fixture(fixture_dir)
            if args.language and fixture.language != args.language:
                continue
            if missing := missing_requirements(fixture):
                print(f"skipping {fixture.id}: needs {', '.join(missing)}")
                continue
            if fixture_dir not in prepared:
                ok, out = prepare(fixture)
                if not ok:
                    sys.exit(f"{fixture.id}: prepare_command failed\n{out}")
                prepared.add(fixture_dir)
            for model in args.models.split(","):
                for mode in args.modes.split(","):
                    for attempt in range(1, args.repeat + 1):
                        record = run_one(task, fixture_dir, args.skill, model, mode,
                                         attempt, args, args.out)
                        records.append(record)
                        with (args.out / "results.jsonl").open("a", encoding="utf-8") as f:
                            f.write(json.dumps(record) + "\n")
    if not records:
        print("nothing ran: check --task and --language")
        return 1
    summary = summarize(records)
    (args.out / "summary.md").write_text(f"# Evals: {args.skill}\n\n{summary}\n", encoding="utf-8")
    print("\n" + summary + f"\n\nResults in {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
