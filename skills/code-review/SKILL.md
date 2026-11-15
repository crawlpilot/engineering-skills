---
name: code-review
description: Review a diff, branch, commit or pull request and report findings by severity. Use when asked to review code, check a change before merge, give feedback on a PR, or assess whether a change is safe to ship. Covers design, correctness, complexity, tests, naming, documentation and deployment safety. Not for writing the fix itself unless asked, and not a substitute for a dedicated security audit.
---

# Code review

The standard: approve a change once it clearly improves the overall health of the code, even if it is not perfect. Block a change that makes the codebase worse. Technical facts and the project's style guide outrank personal preference.

## Read first

1. Read the change description, linked issue or task. Know what the change is meant to do before reading code.
2. Establish the diff: against the merge base for a branch, or the given range. Note its size and which files are generated, vendored or data.
3. Open the reference for the language in use: [Java](references/java.md) or [Python](references/python.md).

## Workflow

1. **Check the shape first.** Does the change do one thing? Does the description match the diff? If it mixes a refactor with a behaviour change, or is too large to review well, say so before anything else and suggest how to split it.
2. **Review the design** before the details. If the approach is wrong, stop and report that; line comments on a design that must change waste everyone's time.
3. **Read the core of the change**, then the rest in dependency order. Read tests alongside the code they cover. Open the surrounding file when the diff alone lacks context.
4. **Walk the checklist** below.
5. **Verify what you can.** Run the tests, the linter and the type checker if available. Trace at least one edge case through the new code by hand.
6. **Classify each finding** and write the review in the report format.

## Checklist

Work top to bottom; earlier items matter more.

1. **Design.** Do the parts interact sensibly? Does this belong here, or in a library or another module? Does it fit the existing architecture?
2. **Functionality.** Does it do what the author intended, and is that good for users and for the next developer? Probe edge cases, error paths, null and empty inputs, concurrency, ordering, and behaviour under retry.
3. **Complexity.** Can each piece be understood quickly? Flag over-engineering: generality, configuration or abstraction for needs that do not exist yet.
4. **Tests.** Are there tests in the same change? Would they fail if the code broke? Do they assert something meaningful? Is anything risky left untested?
5. **Naming.** Do names say what a thing is or does without being unwieldy?
6. **Comments.** Do they explain why, not what? Is there a stale comment or a TODO without an owner? Would simpler code remove the need for the comment?
7. **Style and consistency.** Does it follow the project's style guide and linter? Where the guide is silent, does it match surrounding code?
8. **Documentation.** If the change alters how the code is built, tested, used or released, are the docs updated?
9. **Deployment safety.** Is it covered by existing monitoring and alarms? Can it run alongside the previous version during rollout? Can it be rolled back cleanly, including any data or schema change? Are its dependencies already deployed?
10. **Every line.** Have you read every human-written line you were asked to review? If not, say which parts you did not cover.
11. **Context.** Looking at the whole file and system, does this improve code health or erode it?
12. **Good things.** Note what was done well; it tells the author what to keep doing.

## Severity

- **Blocking:** a bug, data loss or security risk, a broken contract, a missing test for risky logic, or a design that will need rework. Must change before merge.
- **Should fix:** makes the code meaningfully harder to maintain or operate. Fix now or track with an owner.
- **Nit:** optional polish. Prefix with "Nit:" and never block on it.
- **Question:** something you could not determine. Ask; do not assert.

## Writing findings

- Comment on the code, not the author. Give the reason, not just the instruction.
- Point to the file and line, state the problem, show the failing input or scenario, and suggest a direction.
- Be certain or say you are not. Do not report a possible issue as a confirmed one; trace it or label it a question.
- Do not flood the review with nits. If style issues are widespread, say so once and point to the formatter.
- Keep unrelated cleanup out of scope. Suggest it as a follow-up.

## Do not

- Approve what you have not read, or imply coverage you did not give.
- Block on personal taste where the style guide is silent and the code is consistent.
- Demand a rewrite because you would have designed it differently, when the given design works and is maintainable.
- Rewrite the change yourself unless asked to.
- Invent findings to appear thorough. A short review of a good change is a correct review.
- Present this as a security audit. Flag what you see and recommend a specialist review for authentication, cryptography, payments or privacy-sensitive code.

## Report

1. **Verdict:** approve, approve with follow-ups, or request changes, in one sentence with the main reason.
2. **Blocking findings**, then **should fix**, then **nits** and **questions**, each with file and line.
3. **What was verified:** commands run and results.
4. **What was not reviewed**, and why.
5. **Good things**, briefly.

Sources for these rules are in [references/sources.md](references/sources.md).
