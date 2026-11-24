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
evals/<name>/fixtures/            runnable sample projects, graders and known-good answers
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

A skill change should make an agent measurably better at the task. The evals measure that by running the same task with and without the skill, on small real projects in Java, Kotlin and Python. No model judges the work: every check is a build, a test run, a file comparison or a pattern match.

| Skill | Task | What the agent is given | How it's graded |
| --- | --- | --- | --- |
| unit-testing | tier-boundary | A tier lookup whose code makes 51 items bulk while its docs say 50 | Agent's tests run against the correct code, the bug and 6 mutants |
| integration-testing | user-repository | A Postgres repository with SQL migrations (needs Docker) | 5 mutants in the SQL and the migration, which only tests against a real schema catch; container used, no in-memory database |
| code-review | pagination-off-by-one | A feature branch: page 1 skips the first page, an untested branch, two nits | Report names the bug as blocking and the missing test, doesn't approve; code untouched |
| coding-standards | swallowed-errors | A client that catches every exception and returns null | Hidden tests: errors raise with context and cause, in the project's own error type; no broad catch left; nothing else touched |
| design-patterns | type-code-switch | Three switches on one enum, each with a default | Behaviour unchanged (hidden tests); adding a fifth enum value must break the build or tests |
| design-patterns | no-force | A request for a factory and a builder nothing needs | No new classes, code untouched, report declines with the reason |
| sca-fixes | transitive-relock | uv.lock pinning a vulnerable urllib3 (GHSA-pq67-6m6q-mj2v) | urllib3 fixed; requests, other packages and pyproject unchanged |
| sca-fixes | parent-upgrade | okhttp 4.9.0 pulling in a vulnerable okio (GHSA-w33c-445m-f8w7) | okio fixed in the dependency tree, by upgrading okhttp within 4.x, not an override |

**Two kinds of fixture.** A mutation fixture (unit-testing) grades the tests the agent wrote: the grader restores the original implementation, then runs the agent's tests against the correct version, the planted bug and each mutant. A checks fixture grades anything else with typed checks in `fixture.yaml` (`run`, `grep`, `unchanged`, `report`, `ran`, `uv_lock`, `mutation`), each worth points. A failed `gate` check zeroes the score, and `only_if` withholds credit for restraint ("left the manifest alone") until the actual fix is in. The check types are documented at the top of `scripts/evals/checks.py`.

**Fixture self-test.** Before any model is graded, `selftest_fixtures.py` proves each fixture is fair:

- the starting project builds and its tests pass;
- every mutant compiles and survives the project's existing tests, so killing it takes real tests;
- a known-good answer scores 100;
- a known-weak answer, and doing nothing at all, each score 60 or less.

All 21 fixtures pass. The three integration-testing fixtures need Docker, so they self-test in CI.

```bash
pip install -r scripts/requirements.txt
python3 scripts/evals/selftest_fixtures.py                     # all fixtures (JDK 21+, Maven, uv; Docker for integration)
python3 scripts/evals/selftest_fixtures.py --skill sca-fixes --language python
python3 scripts/evals/test_evals.py                            # harness unit tests, no builds

# Model runs: needs ANTHROPIC_API_KEY and the claude CLI
python3 scripts/evals/run_evals.py --skill code-review --models haiku,sonnet,opus --repeat 3
python3 scripts/evals/run_routing.py --model sonnet            # 60 trigger prompts across all skills
python3 scripts/evals/run_routing.py --list                    # show them without running

# Grade any workspace by hand
python3 scripts/evals/grade.py evals/code-review/fixtures/pagination-off-by-one/java path/to/workspace \
    --report report.md --commands commands.txt
```

`run_evals.py` copies the fixture into a fresh git repository (review fixtures get a `feature` branch holding the change), installs the skill under `.claude/skills/` only in "with" mode, and runs Claude Code headless with a throwaway config directory so your own skills and settings don't leak in. Results land in `evals/results/<timestamp>/` (ignored by git) as `results.jsonl`, `summary.md` and one transcript per run.

The `evals` workflow runs every skill nightly, and on demand, once the `ANTHROPIC_API_KEY` repository secret is set; until then it skips. A full nightly run is 21 fixtures x 3 models x 2 modes = 126 agent sessions, each capped at $2 by `--max-budget-usd`. CI on every push runs the self-tests and a pipeline pass with `fake_agent.py`, a stand-in that needs no model.

## License

MIT. See [LICENSE](LICENSE). Source material is paraphrased and linked, not reproduced.
