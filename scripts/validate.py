#!/usr/bin/env python3
"""Validate the skills in this repository. Standard library only.

Checks, per skill folder under skills/:
  - SKILL.md exists and opens with front matter holding `name` and `description`
  - `name` matches the folder name and is kebab-case
  - the description says when to use the skill and stays within length limits
  - SKILL.md is within the line limit and has the required sections
  - references/sources.md exists
  - every relative markdown link in the skill resolves to a file
  - an evals/<name>/cases.md file exists

Exit status is 1 if any error is found.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MAX_CORE_LINES = 200
MIN_DESCRIPTION = 80
MAX_DESCRIPTION = 1024
REQUIRED_SECTIONS = ("## Workflow", "## Do not", "## Report")
TRIGGER_WORDS = ("use when", "use for", "use this")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^(```|~~~)")


def parse_front_matter(text: str) -> tuple[dict[str, str], str | None]:
    """Return (fields, error). Supports single-line `key: value` pairs only."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "missing front matter (file must start with ---)"
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, "front matter is not closed with ---"
    fields: dict[str, str] = {}
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        if ":" not in raw or raw[0].isspace():
            return {}, f"front matter line is not a single-line `key: value`: {raw!r}"
        key, value = raw.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields, None


def strip_code(text: str) -> str:
    """Drop fenced code blocks so example links inside them are not checked."""
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def check_links(md_file: Path, root: Path) -> list[str]:
    errors = []
    for target in LINK_RE.findall(strip_code(md_file.read_text(encoding="utf-8"))):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            continue  # absolute URL, mailto, or in-page anchor
        path = (md_file.parent / target.split("#", 1)[0]).resolve()
        if not path.exists():
            errors.append(f"{md_file.relative_to(root)}: broken link -> {target}")
    return errors


def check_skill(skill_dir: Path, root: Path) -> list[str]:
    errors: list[str] = []
    rel = skill_dir.relative_to(root)
    core = skill_dir / "SKILL.md"
    if not core.is_file():
        return [f"{rel}: SKILL.md is missing"]

    text = core.read_text(encoding="utf-8")
    fields, err = parse_front_matter(text)
    if err:
        errors.append(f"{rel}/SKILL.md: {err}")
    else:
        name = fields.get("name", "")
        desc = fields.get("description", "")
        if not name:
            errors.append(f"{rel}/SKILL.md: front matter has no name")
        elif name != skill_dir.name:
            errors.append(f"{rel}/SKILL.md: name {name!r} does not match folder {skill_dir.name!r}")
        elif not NAME_RE.match(name):
            errors.append(f"{rel}/SKILL.md: name {name!r} is not kebab-case")
        if not desc:
            errors.append(f"{rel}/SKILL.md: front matter has no description")
        else:
            if not MIN_DESCRIPTION <= len(desc) <= MAX_DESCRIPTION:
                errors.append(
                    f"{rel}/SKILL.md: description is {len(desc)} characters "
                    f"(allowed {MIN_DESCRIPTION}-{MAX_DESCRIPTION})"
                )
            if not any(w in desc.lower() for w in TRIGGER_WORDS):
                errors.append(f"{rel}/SKILL.md: description does not say when to use the skill ('Use when ...')")
            if "<" in desc or ">" in desc:
                errors.append(f"{rel}/SKILL.md: description contains angle brackets")

    line_count = len(text.splitlines())
    if line_count > MAX_CORE_LINES:
        errors.append(f"{rel}/SKILL.md: {line_count} lines (limit {MAX_CORE_LINES}); move detail to references/")
    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^{re.escape(section)}\b", text, flags=re.MULTILINE):
            errors.append(f"{rel}/SKILL.md: missing section {section!r}")

    if not (skill_dir / "references" / "sources.md").is_file():
        errors.append(f"{rel}: references/sources.md is missing")
    if not (root / "evals" / skill_dir.name / "cases.md").is_file():
        errors.append(f"evals/{skill_dir.name}/cases.md is missing")

    for md in sorted(skill_dir.rglob("*.md")):
        errors.extend(check_links(md, root))
    return errors


def check_repo(root: Path) -> list[str]:
    errors: list[str] = []
    skills_dir = root / "skills"
    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.is_dir() else []
    if not skill_dirs:
        errors.append("no skill folders found under skills/")
    for skill_dir in skill_dirs:
        errors.extend(check_skill(skill_dir, root))

    for manifest in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
        path = root / manifest
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{manifest}: invalid JSON ({exc})")
    readme = root / "README.md"
    if readme.is_file():
        errors.extend(check_links(readme, root))
    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parent.parent
    errors = check_repo(root)
    for e in errors:
        print(f"ERROR {e}")
    count = len([p for p in (root / "skills").iterdir() if p.is_dir()]) if (root / "skills").is_dir() else 0
    print(f"{count} skill(s) checked, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
