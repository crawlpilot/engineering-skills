"""Check-based fixtures: grade an agent's work with a list of typed checks.

The unit-testing fixtures grade tests by mutation (fixtures.py). Other skills
produce other things: a review report, a dependency fix, a refactor. Their
fixtures list checks in fixture.yaml, each worth some points:

    checks:
      - name: behaviour unchanged
        type: run                # copy the workspace, optionally add files and edit,
        overlay: grading/hidden  # run a command, expect it to pass or fail
        command: mvn -q -B -o test
        expect: pass
        gate: true               # if a gate fails, the score is 0
        points: 40

Check types:
  run        overlay?, edits?, command? (default test_command), expect pass|fail,
             output? (regex the output must match), output_absent? (regex it must not)
  grep       files (glob), pattern (regex), expect present|absent
  unchanged  files (glob): every matching file equals the starting workspace
  report     patterns? (all must match), absent? (none may match); skipped with no report
  ran        pattern: some shell command the agent ran must match; skipped with no transcript
  uv_lock    package, min_version? and/or same_as_start?: reads uv.lock
  mutation   mutants (each: file?, find, replace): the workspace's tests must pass as
             written and fail on each mutant; earns points x share killed

Any check can carry `only_if: <name of another check>`: it then earns nothing
unless that check passed. Use it for restraint ("left the manifest alone"), which
should only count once the actual fix is in; otherwise doing nothing scores well.

Edits ({file, find, replace, regex?}) apply to one file; a regex edit replaces the
first match. An edit whose find text is gone (the agent restructured the code)
fails the check, with a note.

A fixture may have a `change/` directory: the runner commits project/ on main and
then change/ on a `feature` branch, which is how review tasks get a diff to read.
"""
from __future__ import annotations

import re
import subprocess
import tempfile
import tomllib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class CheckResult:
    name: str
    type: str
    points: int
    gate: bool
    passed: bool | None  # None = skipped (no report or transcript to check)
    earned: float
    note: str = ""


@dataclass
class ChecksGrade:
    fixture: str
    checks: list[CheckResult]
    score: int
    notes: list[str]
    outputs: dict[str, str] = field(repr=False, default_factory=dict)

    def to_dict(self, with_outputs: bool = False) -> dict:
        d = asdict(self)
        if not with_outputs:
            d.pop("outputs")
        return d


def starting_workspace(fixture, dst: Path) -> None:
    """What the agent starts from: project/ plus change/ when the fixture has one."""
    from fixtures import copy_tree
    copy_tree(fixture.project, dst)
    if fixture.change and (fixture.root / fixture.change).exists():
        copy_tree(fixture.root / fixture.change, dst)


def _files(base: Path, glob: str) -> dict[str, Path]:
    from fixtures import IGNORED_DIRS, glob_to_regex
    rx = glob_to_regex(glob)
    out = {}
    for p in base.rglob("*"):
        if p.is_file() and not any(part in IGNORED_DIRS for part in p.relative_to(base).parts):
            rel = p.relative_to(base).as_posix()
            if rx.match(rel):
                out[rel] = p
    return out


def _apply_edits(root: Path, edits: list[dict]) -> str | None:
    """Apply edits in place; return an error note if one can't be applied."""
    for e in edits or []:
        path = root / e["file"]
        if not path.exists():
            return f"{e['file']} no longer exists"
        text = path.read_text(encoding="utf-8")
        if e.get("regex"):
            new, n = re.subn(e["find"], e["replace"], text, count=1, flags=re.MULTILINE)
            if n == 0:
                return f"pattern {e['find']!r} not found in {e['file']}"
        else:
            if e["find"] not in text:
                return f"{e['find']!r} not found in {e['file']}"
            new = text.replace(e["find"], e["replace"], 1)
        path.write_text(new, encoding="utf-8")
    return None


def _run_in_copy(fixture, workspace: Path, overlay: str | None, edits: list[dict] | None,
                 command: str) -> tuple[bool | None, str]:
    from fixtures import copy_tree, run
    with tempfile.TemporaryDirectory(prefix=f"{fixture.id}-check-") as tmp:
        t = Path(tmp)
        copy_tree(workspace, t)
        if overlay:
            copy_tree(fixture.root / overlay, t)
        err = _apply_edits(t, edits or [])
        if err:
            return None, err
        return run(fixture.command(command), t)


def _version(v: str) -> tuple:
    return tuple(int(x) if x.isdigit() else 0 for x in re.split(r"[.+-]", v)[:4])


def _uv_lock_versions(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return {p["name"]: p.get("version", "") for p in data.get("package", [])}


def _check(fixture, c: dict, workspace: Path, start: Path, report: str | None,
           commands: list[str] | None) -> tuple[bool | None, float, str, str]:
    """Return (passed, share earned 0..1, note, output)."""
    kind = c["type"]
    if kind == "run":
        ok, out = _run_in_copy(fixture, workspace, c.get("overlay"), c.get("edits"),
                               c.get("command", fixture.test_command))
        if ok is None:
            return False, 0, out, ""
        want_pass = c.get("expect", "pass") == "pass"
        passed = ok == want_pass
        if passed and c.get("output"):
            passed = re.search(c["output"], out, re.MULTILINE) is not None
            if not passed:
                return False, 0, "command output did not match", out
        if passed and c.get("output_absent"):
            hit = re.search(c["output_absent"], out, re.MULTILINE)
            if hit:
                return False, 0, f"command output contains {hit.group(0)!r}", out
        return passed, float(passed), "" if passed else f"expected the command to {c.get('expect', 'pass')}", out

    if kind == "grep":
        rx = re.compile(c["pattern"], re.MULTILINE)
        hits = [rel for rel, p in _files(workspace, c["files"]).items()
                if rx.search(p.read_text(encoding="utf-8", errors="replace"))]
        present = bool(hits)
        passed = present if c.get("expect", "present") == "present" else not present
        note = "" if passed else (f"found in {', '.join(hits)}" if present else "not found")
        return passed, float(passed), note, ""

    if kind == "unchanged":
        before, after = _files(start, c["files"]), _files(workspace, c["files"])
        changed = sorted(rel for rel in set(before) | set(after)
                         if rel not in before or rel not in after
                         or before[rel].read_bytes() != after[rel].read_bytes())
        return not changed, float(not changed), ("changed: " + ", ".join(changed)) if changed else "", ""

    if kind == "report":
        if report is None:
            return None, 0, "no report", ""
        missing = [p for p in c.get("patterns", []) if not re.search(p, report, re.MULTILINE)]
        present = [p for p in c.get("absent", []) if re.search(p, report, re.MULTILINE)]
        passed = not missing and not present
        note = "; ".join(filter(None, [f"missing {missing}" if missing else "",
                                       f"should not say {present}" if present else ""]))
        return passed, float(passed), note, ""

    if kind == "ran":
        if commands is None:
            return None, 0, "no transcript", ""
        passed = any(re.search(c["pattern"], cmd) for cmd in commands)
        return passed, float(passed), "" if passed else "no matching command was run", ""

    if kind == "uv_lock":
        now = _uv_lock_versions(workspace / "uv.lock")
        then = _uv_lock_versions(start / "uv.lock")
        pkg = c["package"]
        version = now.get(pkg)
        if version is None:
            return False, 0, f"{pkg} not in uv.lock", ""
        problems = []
        if c.get("min_version") and _version(version) < _version(c["min_version"]):
            problems.append(f"{pkg} {version} < {c['min_version']}")
        if c.get("same_as_start") and version != then.get(pkg):
            problems.append(f"{pkg} moved {then.get(pkg)} -> {version}")
        return not problems, float(not problems), "; ".join(problems), ""

    if kind == "mutation":
        command = c.get("command", fixture.test_command)
        base_ok, base_out = _run_in_copy(fixture, workspace, None, None, command)
        if not base_ok:
            return False, 0, "tests fail on the unmutated code", base_out
        mutants = c["mutants"]
        with ThreadPoolExecutor(max_workers=4) as pool:
            futs = {m["name"]: pool.submit(_run_in_copy, fixture, workspace, None,
                                           [{"file": m.get("file", c.get("file")), "find": m["find"],
                                             "replace": m["replace"]}], command)
                    for m in mutants}
            res = {n: f.result() for n, f in futs.items()}
        killed = {n: ok is False for n, (ok, _) in res.items()}
        survivors = [n for n, k in killed.items() if not k]
        share = sum(killed.values()) / len(killed)
        return share == 1, share, ("surviving mutants: " + ", ".join(survivors)) if survivors else "", ""

    raise ValueError(f"{fixture.id}: unknown check type {kind!r}")


def grade_checks(fixture, workspace: Path, report: str | None = None,
                 commands: list[str] | None = None) -> ChecksGrade:
    with tempfile.TemporaryDirectory(prefix=f"{fixture.id}-start-") as tmp:
        start = Path(tmp)
        starting_workspace(fixture, start)
        results, outputs = [], {}
        with ThreadPoolExecutor(max_workers=2) as pool:
            futs = [(c, pool.submit(_check, fixture, c, workspace, start, report, commands))
                    for c in fixture.checks]
            for c, fut in futs:
                passed, share, note, out = fut.result()
                points = int(c.get("points", 0))
                results.append(CheckResult(c["name"], c["type"], points, bool(c.get("gate")),
                                           passed, round(points * share, 1), note))
                if out:
                    outputs[c["name"]] = out[-2000:]

    by_name = {r.name: r for r in results}
    for c, r in zip(fixture.checks, results):
        dep = c.get("only_if")
        if not dep:
            continue
        if dep not in by_name:
            raise ValueError(f"{fixture.id}: check {c['name']!r} has only_if {dep!r}, which is not a check")
        if r.passed and not by_name[dep].passed:
            # Still counts as passed for gating; it just earns nothing yet.
            r.earned, r.note = 0, f"no credit until {dep!r} passes"

    notes = []
    counted = [r for r in results if r.passed is not None]
    total = sum(r.points for r in counted)
    gate_failed = [r.name for r in counted if r.gate and not r.passed]
    if gate_failed:
        notes.append("gate failed: " + ", ".join(gate_failed))
        score = 0
    else:
        score = round(100 * sum(r.earned for r in counted) / total) if total else 0
    return ChecksGrade(fixture.id, results, score, notes, outputs)


def git_with_change(fixture, path: Path) -> None:
    """Commit the project on main, then change/ (if any) on a feature branch."""
    from fixtures import copy_tree
    ident = ["-c", "user.email=eval@example.com", "-c", "user.name=eval"]
    def git(*args):
        subprocess.run(["git", *ident, *args], cwd=path, check=True, capture_output=True)
    git("init", "-q", "-b", "main")
    git("add", "-A")
    git("commit", "-q", "-m", "Initial project")
    if fixture.change and (fixture.root / fixture.change).exists():
        git("checkout", "-q", "-b", "feature")
        copy_tree(fixture.root / fixture.change, path)
        git("add", "-A")
        git("commit", "-q", "-m", fixture.change_message or "Add feature")
