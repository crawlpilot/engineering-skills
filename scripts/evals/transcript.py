"""Read a Claude Code `--output-format stream-json` transcript.

Each line is one JSON event. The parts the evals use:
  - assistant messages, whose content holds tool_use blocks (name + input)
  - the final {"type": "result"} event: result text, cost, turns, duration
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Transcript:
    result: str = ""
    is_error: bool = False
    cost_usd: float = 0.0
    turns: int = 0
    duration_ms: int = 0
    tool_uses: list[dict] = field(default_factory=list)

    @property
    def bash_commands(self) -> list[str]:
        return [t["input"].get("command", "") for t in self.tool_uses if t["name"] == "Bash"]

    @property
    def files_read(self) -> list[str]:
        return [t["input"].get("file_path", "") for t in self.tool_uses if t["name"] == "Read"]

    def skills_used(self) -> set[str]:
        """Skills the agent invoked, by the Skill tool or by reading a SKILL.md."""
        used = {str(t["input"].get("skill", "")).split(":")[-1]
                for t in self.tool_uses if t["name"] == "Skill"}
        for path in self.files_read + self.bash_commands:
            marker = "/.claude/skills/"
            if marker in path and "SKILL.md" in path:
                used.add(path.split(marker, 1)[1].split("/", 1)[0])
        used.discard("")
        return used

    def references_read(self) -> list[str]:
        return [p.split("/.claude/skills/", 1)[1] for p in self.files_read
                if "/.claude/skills/" in p]


def parse(text: str) -> Transcript:
    t = Transcript()
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []) or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    t.tool_uses.append({"name": block.get("name", ""),
                                        "input": block.get("input", {}) or {}})
        elif event.get("type") == "result":
            t.result = event.get("result", "") or ""
            t.is_error = bool(event.get("is_error"))
            t.cost_usd = float(event.get("total_cost_usd", 0) or 0)
            t.turns = int(event.get("num_turns", 0) or 0)
            t.duration_ms = int(event.get("duration_ms", 0) or 0)
    return t


def load(path: Path) -> Transcript:
    return parse(path.read_text(encoding="utf-8"))
