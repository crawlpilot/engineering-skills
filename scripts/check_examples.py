#!/usr/bin/env python3
"""Syntax-check every fenced code example in the skills.

Each ```java, ```kotlin, ```python, ```ts, ```json, ```toml and ```xml block under
skills/ is parsed. Snippets are often fragments (a method, a few statements), so a
block that fails as a whole file is retried inside a minimal wrapper: a class body
for Java, a function body for Kotlin and Python. A block passes if any form parses.

This is a syntax check, not a compile: it catches typos, unbalanced braces and
broken annotations, not unknown types. Full compilation happens in the eval
fixtures (evals/*/fixtures), which are real projects.

To exempt a block that is deliberately invalid (for example a "don't do this"
example that does not parse), put `<!-- example: no-check -->` on the line
directly above its opening fence.

Usage:
    python3 scripts/check_examples.py            # all skills
    python3 scripts/check_examples.py skills/unit-testing

Needs: pip install tree-sitter-language-pack  (Java, Kotlin, TypeScript parsing)
Exit status is 1 if any block fails.
"""
from __future__ import annotations

import ast
import json
import sys
import textwrap
import tomllib
import xml.dom.minidom
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_MARKER = "<!-- example: no-check -->"
LANG_ALIASES = {
    "java": "java",
    "kotlin": "kotlin",
    "kt": "kotlin",
    "kts": "kotlin",
    "python": "python",
    "py": "python",
    "ts": "typescript",
    "typescript": "typescript",
    "js": "javascript",
    "javascript": "javascript",
    "json": "json",
    "toml": "toml",
    "xml": "xml",
}


@dataclass
class Block:
    path: Path
    line: int  # 1-based line of the opening fence
    lang: str
    code: str


def extract_blocks(path: Path) -> list[Block]:
    blocks: list[Block] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("```") and len(stripped) > 3:
            fence_line = i
            info = stripped[3:].strip().split()[0].lower()
            body: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            skipped = fence_line > 0 and lines[fence_line - 1].strip() == SKIP_MARKER
            lang = LANG_ALIASES.get(info)
            if lang and not skipped:
                blocks.append(Block(path, fence_line + 1, lang, "\n".join(body)))
        elif stripped.startswith("```"):
            # Unlabelled fence: skip to its close.
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                i += 1
        i += 1
    return blocks


# --- parsers ---------------------------------------------------------------

_TS_PARSERS: dict[str, object] = {}


def _tree_sitter(lang: str):
    if lang not in _TS_PARSERS:
        try:
            from tree_sitter_language_pack import get_parser
        except ImportError:
            sys.exit(
                "check_examples.py needs tree-sitter-language-pack: "
                "pip install tree-sitter-language-pack"
            )
        _TS_PARSERS[lang] = get_parser(lang)
    return _TS_PARSERS[lang]


def _first_error(node) -> tuple[int, str] | None:
    """Depth-first search for an ERROR or MISSING node; returns (row, kind)."""
    stack = [node]
    while stack:
        n = stack.pop()
        if n.type == "ERROR" or n.is_missing:
            return n.start_point[0], ("missing " + n.type) if n.is_missing else "syntax error"
        stack.extend(reversed(n.children))
    return None


def _ts_parse(lang: str, code: str) -> tuple[int, str] | None:
    tree = _tree_sitter(lang).parse(code.encode("utf-8"))
    return _first_error(tree.root_node)


def check_java(code: str) -> str | None:
    attempts = [
        (code, 0),
        ("class Example__ {\n" + code + "\n}", 1),
        ("class Example__ { void example__() throws Exception {\n" + code + "\n} }", 1),
    ]
    return _try_forms("java", attempts)


def check_kotlin(code: str) -> str | None:
    attempts = [
        (code, 0),
        ("fun example__() {\n" + code + "\n}", 1),
        ("class Example__ {\n" + code + "\n}", 1),
    ]
    return _try_forms("kotlin", attempts)


def check_typescript(code: str, lang: str) -> str | None:
    return _try_forms(lang, [(code, 0)])


def _try_forms(lang: str, attempts: list[tuple[str, int]]) -> str | None:
    first_failure = None
    for source, offset in attempts:
        err = _ts_parse(lang, source)
        if err is None:
            return None
        if first_failure is None:
            first_failure = f"line +{err[0] - offset + 1}: {err[1]}"
    return first_failure


def check_python(code: str) -> str | None:
    dedented = textwrap.dedent(code)
    for source in (dedented, "async def example__():\n" + textwrap.indent(dedented, "    ")):
        try:
            ast.parse(source)
            return None
        except SyntaxError as exc:
            last = f"line +{exc.lineno}: {exc.msg}"
    return last


def check_json(code: str) -> str | None:
    try:
        json.loads(code)
        return None
    except json.JSONDecodeError as exc:
        return f"line +{exc.lineno}: {exc.msg}"


def check_toml(code: str) -> str | None:
    try:
        tomllib.loads(code)
        return None
    except tomllib.TOMLDecodeError as exc:
        return str(exc)


def check_xml(code: str) -> str | None:
    # Snippets are usually one or more sibling elements, so wrap them.
    try:
        xml.dom.minidom.parseString("<root__>" + code + "</root__>")
        return None
    except Exception as exc:  # expat raises its own error type
        return str(exc)


def check(block: Block) -> str | None:
    if block.lang == "java":
        return check_java(block.code)
    if block.lang == "kotlin":
        return check_kotlin(block.code)
    if block.lang == "python":
        return check_python(block.code)
    if block.lang in ("typescript", "javascript"):
        return check_typescript(block.code, block.lang)
    if block.lang == "json":
        return check_json(block.code)
    if block.lang == "toml":
        return check_toml(block.code)
    if block.lang == "xml":
        return check_xml(block.code)
    return None


def main(argv: list[str]) -> int:
    targets = [Path(a).resolve() for a in argv] or [ROOT / "skills"]
    files = sorted(
        p for t in targets for p in ([t] if t.is_file() else t.rglob("*.md"))
    )
    counts: dict[str, int] = {}
    failures: list[str] = []
    for path in files:
        for block in extract_blocks(path):
            counts[block.lang] = counts.get(block.lang, 0) + 1
            error = check(block)
            if error:
                rel = path.relative_to(ROOT)
                failures.append(f"{rel}:{block.line} [{block.lang}] {error}")
    summary = ", ".join(f"{n} {lang}" for lang, n in sorted(counts.items()))
    print(f"Checked {sum(counts.values())} blocks ({summary}).")
    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        print(f"{len(failures)} block(s) failed. Fix them, or mark a deliberate "
              f"counter-example with {SKIP_MARKER!r} on the line above its fence.")
        return 1
    print("All examples parse.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
