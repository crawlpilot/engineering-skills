---
name: unit-testing
description: Write, extend or repair unit tests for a function, class or module. Use when asked to add tests, raise coverage, test a bug fix or make code testable, or when new or changed logic has no test. Covers choosing cases, structure, test doubles and proving the tests can fail. Not for tests that need a real database, network or another service; use integration-testing for those.
---

# Unit testing

A unit test earns its place only if it fails when the behaviour breaks and stays green when the implementation is refactored. Work toward that, not toward a coverage number.

## Read first

1. Open the code under test and two or three existing test files near it. Match their framework, naming, fixtures, assertion style and file layout.
2. Find the test command in the build file, task runner or CI config, and run the existing suite once so you know the baseline.
3. Open the reference for the language in use: [Java](references/java.md) or [Python](references/python.md). For other languages, apply this file and the repo's own conventions.

## Workflow

1. **List behaviours, not methods.** Write down what the unit promises: each class of input, each branch that changes the result, each error it raises, each side effect a caller relies on. One behaviour becomes one test.
2. **Choose cases** with the checklist below.
3. **For a bug fix, write the failing test first.** It must reproduce the bug and fail on the current code before you touch the fix.
4. **Write each test** as arrange, act, assert, with a name that states the action and the expected outcome.
5. **Prove each new test can fail.** Break the code under test (flip a condition, return early, change a constant), confirm the test fails for the intended reason, then restore the code. A test never seen failing is unverified.
6. **Run the whole suite**, not only the new file.
7. **Report** as described at the end.

## Case checklist

For every behaviour, include what applies:

- A typical valid input.
- Boundaries: empty, one, many; zero, negative, maximum; first and last; exactly at a limit and one past it.
- Invalid input: wrong type, null, malformed, out of range. Assert the specific error, not just that something was thrown.
- Each branch of a conditional that changes the outcome.
- State: first call versus repeated call, idempotence, ordering.
- Time, randomness, locale and timezone: inject or freeze them. Never read the real clock.

Skip trivial accessors, framework glue and generated code.

## Structure rules

- **Test through the public API.** Call the unit the way its real callers do. Do not reach into private members.
- **Test state, not interactions.** Assert on returned values and observable effects. Verify a call to a collaborator only when that call is the behaviour, such as "an email was sent".
- **One behaviour per test.** One action, one outcome. Needing "and" in the name usually means two tests. Several assertions are fine when they describe a single outcome.
- **No logic in tests.** No loops building expectations, no conditionals, no computed strings. Use parameterised tests when one shape repeats with different data.
- **Literal expected values.** Do not recompute the expectation with the production formula.
- **Descriptive over deduplicated.** Keep everything needed to understand a test inside its body. Extract a helper only when it removes noise without hiding a value the test depends on.
- **Build test data with helpers that take overrides**, so each test states only the fields it cares about. Avoid vague shared constants.
- **Clear failure output.** A failure should show expected, actual and the relevant inputs without opening the test.
- **Independent and hermetic.** No shared mutable state, no dependence on order, no network, no sleeps, no files outside a temporary directory.

## Test doubles

Prefer, in order: the real collaborator when it is fast and deterministic; a hand-written fake such as an in-memory repository or fixed clock; a stub returning canned data; a mock that verifies an interaction.

Put doubles only at boundaries the code owns: an HTTP client wrapper, a repository interface, a clock. Do not mock the unit under test, value objects or third-party internals. If a test needs more than two or three doubles, the unit has too many dependencies. Say so and propose the seam instead of writing a mock-heavy test.

## When code is hard to test

Name the obstacle (hidden global, constructor doing I/O, static call, clock read inline) and propose the smallest change that creates a seam: pass the dependency in, extract the pure calculation, wrap the external call. Make that change only if testability work was requested or is clearly in scope. Otherwise test what is reachable and flag the rest.

## Do not

- Weaken, skip or delete a failing test to get a green run. If an existing test is wrong, explain why before changing it.
- Change a test because of a refactor. Tests change when required behaviour changes.
- Edit production code to match a wrong expectation, or the reverse, without saying which one was wrong.
- Introduce a second test framework, assertion library or mocking library.
- Use snapshot tests for logic. Snapshots suit stable rendered output only.
- Say tests pass without having run them. If they cannot be run here, say so and give the command.

## Report

State: the tests added and the behaviours they cover; the command run and its result; that each new test was seen failing; anything left untested and why; any production bug the tests exposed.

Sources for these rules are in [references/sources.md](references/sources.md).
