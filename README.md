# engineering-skills

Agent skills that encode published engineering practice across the development lifecycle. Each skill is a short, language-neutral workflow with per-language reference files, and every rule traces to a source listed in that skill's `references/sources.md`.

## Status

Batch one of four. Six skills, each with Java, Kotlin, Python and JavaScript/TypeScript references.

| Skill | Use it when |
| --- | --- |
| [unit-testing](skills/unit-testing/SKILL.md) | Adding or repairing tests for a function, class or module |
| [integration-testing](skills/integration-testing/SKILL.md) | Testing across a real boundary: database, HTTP, queue, another service |
| [code-review](skills/code-review/SKILL.md) | Reviewing a diff, branch or pull request |
| [coding-standards](skills/coding-standards/SKILL.md) | Writing or changing production code |
| [design-patterns](skills/design-patterns/SKILL.md) | Deciding how to structure code, or whether a pattern is warranted |
| [sca-fixes](skills/sca-fixes/SKILL.md) | Fixing a vulnerable dependency reported by a scanner |

Planned: change-authoring, dependency-hygiene, security-review, design-doc, api-design, ci-pipeline, safe-deploy, rollback-safety, observability, debugging, postmortem.

## Layout

```text
skills/<name>/SKILL.md            workflow, checklist, do-not rules, report format
skills/<name>/references/java.md  idioms, frameworks, commands (loaded on demand)
skills/<name>/references/kotlin.md
skills/<name>/references/python.md
skills/<name>/references/javascript-typescript.md
skills/<name>/references/sources.md  where each rule comes from
evals/<name>/cases.md             trigger prompts and task checks for the skill
scripts/validate.py               structure and link checks, run in CI
```

## Install

As a Claude Code plugin, from a clone of this repository:

```text
/plugin marketplace add <path-or-owner/repo>
/plugin install engineering-skills
```

Or copy any folder under `skills/` into your agent's skills directory (for Claude Code, `~/.claude/skills/` or a project's `.claude/skills/`). The folders follow the common `SKILL.md` layout, so other agents that read that format can use them unchanged.

The plugin manifest and install commands above follow the documented plugin layout but have not been exercised against a live install from this repository yet.

## Design rules

- **Repo conventions win.** Every skill starts by reading the project's own configuration and nearby code, and follows that over any default here.
- **Verification is a step, not a hope.** Every workflow ends by running something and reporting the result, or saying plainly that it could not be run.
- **No rule without a source.** `sources.md` in each skill says which published practice a rule encodes, and marks anything that comes from general knowledge instead.
- **Small cores.** `SKILL.md` stays under 200 lines; detail lives in references that load only when needed.
- **Skills refuse as well as act.** Each has a "Do not" section for the failure modes worth declining, such as weakening a failing test or adding a pattern nothing needs yet.

## Validate

```bash
python3 scripts/validate.py
```

Checks front matter, description quality, line limits, required sections and relative links. CI runs it on every push and pull request.

## Evals

`evals/<name>/cases.md` lists prompts that should and should not trigger each skill, plus task cases with a pass checklist. They are written cases, not yet an automated harness, and the sample repositories they describe are not included in this batch.

## License

MIT. See [LICENSE](LICENSE). Source material is paraphrased and linked, not reproduced.
