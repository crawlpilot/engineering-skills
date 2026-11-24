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
evals/<name>/cases.yaml           machine-readable tasks for the eval runner
evals/<name>/fixtures/            runnable sample projects with a planted defect
scripts/validate.py               structure and link checks, run in CI
scripts/check_examples.py         syntax check of every code example, run in CI
scripts/evals/                    eval runner, grader, routing test, fixture self-test
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
pip install -r scripts/requirements.txt
python3 scripts/validate.py          # front matter, descriptions, line limits, sections, links
python3 scripts/check_examples.py    # every java, kotlin, python, ts, json, toml, xml block parses
```

CI runs both on every push and pull request. `check_examples.py` is a syntax check: snippets are fragments, so it parses them inside a minimal wrapper when needed. Compiling against real dependencies happens in the eval fixtures.

## Evals

A skill change should make an agent measurably better at the task. The evals measure that by running the same task with and without the skill.

**Fixtures.** Each task runs on small, real projects in Java, Kotlin and Python with one planted defect. The first is `evals/unit-testing/fixtures/tier-boundary`: a price-tier lookup whose code says 51 items is bulk while its docs say 50.

**Grading is mutation-based, not judged by a model.** The grader restores the original implementation, then runs the agent's tests against the correct version, the planted bug, and six mutants. A score out of 100:

| Points | For |
| --- | --- |
| gate | Tests were added and pass on the correct implementation (otherwise 0) |
| 40 | The tests fail on the planted bug |
| 50 | Share of mutants the tests kill |
| 10 | The final report names the bug |

Tests that pass on the buggy code and fail on the correct code are flagged as having encoded the bug.

**Fixture self-test.** Before any model is graded, `selftest_fixtures.py` proves each fixture is fair: a known-good suite scores 100 and kills every mutant, and a typical-values-only suite scores below 60. Today all three tier-boundary fixtures score 100 and 9.

```bash
python3 scripts/evals/selftest_fixtures.py                     # all fixtures (needs JDK 21+ and Maven)
python3 scripts/evals/test_evals.py                            # harness unit tests, no builds

# Model runs: needs ANTHROPIC_API_KEY and the claude CLI
python3 scripts/evals/run_evals.py --skill unit-testing --models haiku,sonnet,opus --repeat 3
python3 scripts/evals/run_routing.py --model sonnet            # 60 trigger prompts across all skills
python3 scripts/evals/run_routing.py --list                    # show them without running

# Grade any workspace by hand
python3 scripts/evals/grade.py evals/unit-testing/fixtures/tier-boundary/java path/to/workspace
```

`run_evals.py` copies the fixture into a fresh git repository, installs the skill under `.claude/skills/` only in "with" mode, and runs Claude Code headless with a throwaway config directory so your own skills and settings don't leak in. Results land in `evals/results/<timestamp>/` (ignored by git) as `results.jsonl`, `summary.md` and one transcript per run.

The `evals` workflow runs the matrix nightly and on demand once the `ANTHROPIC_API_KEY` repository secret is set; until then it skips. CI on every push runs the self-tests and a full pipeline pass with `fake_agent.py`, a stand-in that needs no model.

Status: unit-testing has automated fixtures in all three languages. The other five skills still have written cases only in `cases.md`; their fixtures come next.

## License

MIT. See [LICENSE](LICENSE). Source material is paraphrased and linked, not reproduced.
