"""Load eval fixtures and grade an agent's work on them.

A fixture is a directory holding:

    fixture.yaml   what to run and how to grade (see evals/unit-testing/fixtures/*/java)
    project/       the code the agent is given
    change/        optional: files committed on a `feature` branch (review tasks)
    selftest/      known-good (strong/) and known-weak (weak/) answers

There are two kinds. A mutation fixture (it has `reference`) grades the tests the
agent wrote; that is what this module does. A checks fixture (it has `checks`)
grades anything else with typed checks; see checks.py. `grade_any` picks.

Grading never trusts the agent's copy of the implementation under test. For each
variant (reference, planted bug, every mutant) it copies the agent's workspace,
writes that variant of the implementation from the pristine project file, and runs
the test command. A good suite passes on the reference and fails on everything else.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

# Directories never copied into a grading run: build output and caches.
IGNORED_DIRS = {".git", "target", "build", ".gradle", "__pycache__", ".pytest_cache",
                ".venv", "node_modules", ".claude"}
TEST_TIMEOUT_SECONDS = 600  # a cold Maven or Gradle run on CI can take minutes
MAX_PARALLEL_RUNS = 4  # enough to overlap JVM start-up without starving CI runners


@dataclass
class Replacement:
    find: str
    replace: str

    def apply(self, text: str, where: str) -> str:
        count = text.count(self.find)
        if count != 1:
            raise ValueError(f"{where}: expected {self.find!r} exactly once, found {count}")
        return text.replace(self.find, self.replace)


@dataclass
class Mutant(Replacement):
    name: str = ""


@dataclass
class Fixture:
    root: Path
    id: str
    language: str
    test_command: str
    implementation: str = ""
    tests: str = ""
    reference: Replacement | None = None
    mutants: list[Mutant] = field(default_factory=list)
    prepare_command: str | None = None
    bug_report_patterns: list[str] = field(default_factory=list)
    checks: list[dict] = field(default_factory=list)
    change: str | None = None
    change_message: str | None = None
    requires: list[str] = field(default_factory=list)

    @property
    def kind(self) -> str:
        return "mutation" if self.reference else "checks"

    @property
    def project(self) -> Path:
        return self.root / "project"

    def pristine_implementation(self) -> str:
        return (self.project / self.implementation).read_text(encoding="utf-8")

    def variants(self) -> dict[str, str]:
        """Implementation text for: reference, planted bug, and each mutant."""
        buggy = self.pristine_implementation()
        reference = self.reference.apply(buggy, f"{self.id} reference")
        out = {"reference": reference, "planted-bug": buggy}
        for m in self.mutants:
            out[f"mutant:{m.name}"] = m.apply(reference, f"{self.id} mutant {m.name}")
        return out

    def command(self, template: str) -> str:
        return template.format(python=sys.executable)


def load_fixture(root: Path) -> Fixture:
    data = yaml.safe_load((root / "fixture.yaml").read_text(encoding="utf-8"))
    fixture = Fixture(
        root=root,
        id=data["id"],
        language=data["language"],
        test_command=data["test_command"],
        implementation=data.get("implementation", ""),
        tests=data.get("tests", ""),
        prepare_command=data.get("prepare_command"),
        reference=Replacement(**data["reference"]) if "reference" in data else None,
        mutants=[Mutant(find=m["find"], replace=m["replace"], name=m["name"])
                 for m in data.get("mutants", [])],
        bug_report_patterns=data.get("bug_report_patterns", []),
        checks=data.get("checks", []),
        change=data.get("change"),
        change_message=data.get("change_message"),
        requires=data.get("requires", []),
    )
    if not fixture.reference and not fixture.checks:
        raise ValueError(f"{root}: a fixture needs `reference` (mutation) or `checks`")
    return fixture


def copy_tree(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(*IGNORED_DIRS))


def run(command: str, cwd: Path) -> tuple[bool, str]:
    try:
        proc = subprocess.run(command, shell=True, cwd=cwd, capture_output=True,
                              text=True, timeout=TEST_TIMEOUT_SECONDS,
                              env=env_without_secrets())
    except subprocess.TimeoutExpired:
        return False, f"timed out after {TEST_TIMEOUT_SECONDS}s"
    output = (proc.stdout + proc.stderr)[-4000:]
    return proc.returncode == 0, output


def prepare(fixture: Fixture) -> tuple[bool, str]:
    """Warm dependency caches so graded runs can work offline."""
    if not fixture.prepare_command:
        return True, ""
    from checks import starting_workspace
    with tempfile.TemporaryDirectory(prefix=f"{fixture.id}-prepare-") as tmp:
        starting_workspace(fixture, Path(tmp))
        return run(fixture.command(fixture.prepare_command), Path(tmp))


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a path glob where `**/` matches zero or more directories.

    Also supports one level of braces: `{src,tests}/**`.
    """
    out, i = [], 0
    while i < len(pattern):
        if pattern[i] == "{" and "}" in pattern[i:]:
            end = pattern.index("}", i)
            options = pattern[i + 1:end].split(",")
            out.append("(?:" + "|".join(re.escape(o) for o in options) + ")")
            i = end + 1
        elif pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def test_files(fixture: Fixture, workspace: Path) -> dict[str, str]:
    """Test files in the workspace that are new or changed relative to the project.

    Returns {relative path: "added" | "changed"}.
    """
    found: dict[str, str] = {}
    matcher = glob_to_regex(fixture.tests)
    for path in workspace.rglob("*"):
        if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
            continue
        rel = path.relative_to(workspace).as_posix()
        if not matcher.match(rel):
            continue
        original = fixture.project / rel
        if not original.exists():
            found[rel] = "added"
        elif original.read_bytes() != path.read_bytes():
            found[rel] = "changed"
    return found


@dataclass
class Grade:
    fixture: str
    test_files: dict[str, str]
    passes_on_reference: bool
    catches_planted_bug: bool
    encodes_bug: bool
    mutants_killed: dict[str, bool]
    implementation_changed: bool
    report_names_bug: bool | None
    score: int
    notes: list[str]
    outputs: dict[str, str] = field(repr=False, default_factory=dict)

    @property
    def mutation_score(self) -> float:
        if not self.mutants_killed:
            return 0.0
        return sum(self.mutants_killed.values()) / len(self.mutants_killed)

    def to_dict(self, with_outputs: bool = False) -> dict:
        d = asdict(self)
        d["mutation_score"] = round(self.mutation_score, 3)
        if not with_outputs:
            d.pop("outputs")
        return d


def _run_variant(fixture: Fixture, workspace: Path, text: str) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix=f"{fixture.id}-grade-") as tmp:
        tmp_path = Path(tmp)
        copy_tree(workspace, tmp_path)
        (tmp_path / fixture.implementation).write_text(text, encoding="utf-8")
        return run(fixture.command(fixture.test_command), tmp_path)


def grade(fixture: Fixture, workspace: Path, report: str | None = None) -> Grade:
    """Grade the tests in `workspace` against the fixture's variants.

    Score, out of 100:
      gate  tests were added and pass on the correct implementation, else 0
      40    the suite fails on the planted bug
      50    share of mutants killed
      10    the final report names the planted bug (skipped, and scaled up, if no report)
    """
    notes: list[str] = []
    files = test_files(fixture, workspace)
    impl_now = workspace / fixture.implementation
    implementation_changed = (impl_now.exists() and
                              impl_now.read_text(encoding="utf-8") != fixture.pristine_implementation())
    report_names_bug = None
    if report is not None:
        report_names_bug = all(re.search(p, report) for p in fixture.bug_report_patterns)

    if not files:
        notes.append("no test files were added or changed")
        return Grade(fixture.id, files, False, False, False, {}, implementation_changed,
                     report_names_bug, 0, notes)

    variants = fixture.variants()
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_RUNS) as pool:
        futures = {name: pool.submit(_run_variant, fixture, workspace, text)
                   for name, text in variants.items()}
        results = {name: f.result() for name, f in futures.items()}

    outputs = {name: out for name, (_, out) in results.items()}
    passes_on_reference = results["reference"][0]
    passes_on_bug = results["planted-bug"][0]
    catches_bug = not passes_on_bug
    encodes_bug = passes_on_bug and not passes_on_reference
    killed = {name.removeprefix("mutant:"): not ok
              for name, (ok, _) in results.items() if name.startswith("mutant:")}

    if encodes_bug:
        notes.append("tests pass on the buggy code and fail on the correct code: the bug was encoded as expected behaviour")
    elif not passes_on_reference:
        notes.append("tests fail on the correct implementation (wrong expectation, or they do not compile)")

    score = 0
    if passes_on_reference:
        report_points = 10 if report is not None else 0
        scale = 100 / (90 + report_points)
        raw = (40 if catches_bug else 0) + 50 * (sum(killed.values()) / max(len(killed), 1))
        raw += 10 if report_names_bug else 0
        score = round(raw * scale)
    survivors = [n for n, k in killed.items() if not k]
    if survivors:
        notes.append("surviving mutants: " + ", ".join(survivors))

    return Grade(fixture.id, files, passes_on_reference, catches_bug, encodes_bug, killed,
                 implementation_changed, report_names_bug, score, notes, outputs)


def grade_any(fixture: Fixture, workspace: Path, report: str | None = None,
              commands: list[str] | None = None):
    """Grade with whichever method the fixture uses. Both results have .score and .to_dict()."""
    if fixture.kind == "mutation":
        return grade(fixture, workspace, report=report)
    from checks import grade_checks
    return grade_checks(fixture, workspace, report=report, commands=commands)


def missing_requirements(fixture: Fixture) -> list[str]:
    """Requirements in fixture.yaml (e.g. docker) not available on this machine."""
    missing = []
    for tool in ("uv", "mvn"):
        if tool in fixture.requires and not shutil.which(tool):
            missing.append(tool)
    if "docker" in fixture.requires:
        ok = subprocess.run("docker info", shell=True, capture_output=True).returncode == 0
        if not ok:
            missing.append("docker")
    return missing


def find_fixtures(root: Path) -> list[Path]:
    return sorted(p.parent for p in root.rglob("fixture.yaml"))


def env_without_secrets() -> dict[str, str]:
    """Environment for test commands: drop API keys so fixture code can't read them."""
    return {k: v for k, v in os.environ.items() if "API_KEY" not in k and "TOKEN" not in k}
