---
name: coding-standards
description: Write or change production code so it follows the project's conventions and the language's established style guide. Use when implementing a feature, fixing a bug, refactoring, or when asked to clean up, format, lint or make code idiomatic. Covers discovering repo conventions, naming, error handling, comments, and running the formatter, linter and type checker. Not for choosing an architecture or pattern; use design-patterns for that.
---

# Coding standards

Code is read far more often than it is written. The order of authority is: the repository's own configuration and conventions, then the language's published style guide, then consistency with the surrounding code. Personal preference is not on the list.

## Read first

1. Find the project's rules: formatter and linter configuration, editor config, type-checker settings, contributing guide, and any agent instruction file.
2. Find the commands for format, lint, type check, build and test in the build file, task runner or CI config.
3. Read the file you are changing in full, and one or two neighbours, before editing. Note naming, error handling, logging and layout.
4. Open the reference for the language in use: [Java](references/java.md), [Kotlin](references/kotlin.md), [Python](references/python.md) or [JavaScript and TypeScript](references/javascript-typescript.md).

## Workflow

1. **State the change in one sentence.** If it needs "and", consider two changes.
2. **Make the smallest change that does it.** Do not reformat untouched lines, rename unrelated things or reorganise files along the way.
3. **Write it the way the file already does it.** Match existing patterns for errors, logging, dependency access and tests, even where you would choose differently.
4. **Apply the rules below** as you write.
5. **Run the formatter, linter and type checker** the project uses, and fix what they report in the code you touched.
6. **Build and run the tests** that cover the change.
7. **Reread your own diff** before reporting. Remove debug output, commented-out code and accidental changes.
8. **Report** as described at the end.

## Rules

**Naming**

- Follow the language's case conventions exactly; the reference file lists them.
- Name things for what they are or do. Avoid abbreviations that are not already common in the codebase, and avoid type information in names.
- One-character names only for short loop counters and established notation.

**Functions and structure**

- A function does one thing at one level of abstraction. If it needs a comment to separate its sections, it is probably two functions.
- Keep parameter lists short. Group related values into a type when three or more travel together.
- Return early on invalid input instead of nesting.
- Prefer immutable values and narrow scope. Avoid mutable global state.
- Do not add configuration, parameters, layers or generality for a need that does not exist yet.

**Errors**

- Never swallow an error. Handle it, wrap it with context and rethrow, or let it propagate. An intentionally empty handler needs a comment saying why.
- Catch the narrowest type that the code can actually handle.
- Validate at the boundary: public entry points and anything receiving external input.
- Error messages state what was expected and what was received, and are easy to search for.
- Release resources deterministically with the language's scoped construct.

**Comments and documentation**

- Comments explain why, not what. If a comment restates the code, delete it. If it explains confusing code, simplify the code first.
- Document public APIs in the language's standard doc format: what it does, parameters, return value, errors.
- A TODO names an owner or a tracking reference.

**Dependencies and scope**

- Do not add a dependency for something the standard library or an existing dependency already does.
- Do not introduce a second tool for a job the project already has a tool for.
- Leave formatting-only cleanup of existing code to a separate change.

## Do not

- Reformat or restyle code outside the change.
- Disable a lint rule, add a suppression or loosen a type to make a check pass, without a stated reason next to it.
- Leave commented-out code, debug prints or unused imports.
- Override the project's configured style with a different guide's rule.
- Report the change as complete without running the project's checks. If they cannot be run here, say so and give the commands.

## Report

State: what changed, in a sentence; the format, lint, type-check and test commands run, and their results; any suppression added and why; any convention conflict you found and how you resolved it; anything deliberately left out of scope.

Sources for these rules are in [references/sources.md](references/sources.md).
