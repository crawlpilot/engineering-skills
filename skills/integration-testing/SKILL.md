---
name: integration-testing
description: Write or repair tests that cross a real boundary such as a database, HTTP API, message queue, filesystem or another service. Use when asked for integration, component, contract or API tests, when a change touches persistence or a network call, or when unit tests pass but components fail together. Not for pure logic that needs no real dependency; use unit-testing for that.
---

# Integration testing

Integration tests exist to catch what unit tests cannot: drift between a mock and the real thing, configuration and wiring errors, serialisation mismatches, and behaviour that only appears when components meet. They cost more to run and maintain, so write the fewest that cover the seams, and make each one reliable.

## Read first

1. Find how the repo already runs integration tests: a separate source set, marker or tag, a compose file, container fixtures, a CI job. Follow it.
2. Find how to start dependencies locally, and what the pipeline provides.
3. Open the reference for the language in use: [Java](references/java.md), [Kotlin](references/kotlin.md), [Python](references/python.md) or [JavaScript and TypeScript](references/javascript-typescript.md).

## Workflow

1. **Name the seam.** State which boundary this test proves: "our repository against real PostgreSQL", "our client against the payment API contract". One seam per test class or module.
2. **Pick the smallest real system** that exercises that seam. Prefer the real dependency in a container over an in-memory substitute for it, because fidelity is the point. Replace everything that is not the seam with fakes.
3. **Make it hermetic.** The test starts what it needs, seeds its own data, and cleans up. No shared staging environment, no reliance on data left by another test, no calls to third-party production endpoints.
4. **Write the cases** from the checklist below. Drive the system through its real entry point and assert on observable results: the response, the stored row, the published message.
5. **Remove nondeterminism.** Wait on a condition with a timeout instead of sleeping. Fix clocks and random seeds. Use unique identifiers per test so runs can execute in parallel.
6. **Run it at least three times in a row**, and once in a random order if the runner supports it. A test that fails once in three is not finished.
7. **Tag it** so it runs in the integration stage, not with the fast unit suite, and confirm the pipeline runs that stage.
8. **Report** as described at the end.

## Case checklist

- The main success path, end to end through the seam.
- Negative paths: invalid input rejected, not-found, conflict, permission denied.
- The dependency failing: timeout, connection refused, error response, partial result. Assert the caller's behaviour: retry, fallback, surfaced error.
- Data shape at the boundary: nulls, empty collections, large payloads, Unicode, timezones, numeric precision.
- Idempotence and duplicates for anything retried or delivered at least once.
- Transactions: a failure midway leaves no partial write.
- Schema and migrations: the test runs against the schema the migrations produce, not a hand-built one.
- Backward compatibility when a contract changes: the old reader with the new writer, and the reverse.

## Doubles at the boundary

When the real dependency cannot run in a test (a third-party API, a paid service), stub it at the network level, not inside your client code, so serialisation and error handling are still exercised.

A stub is a claim about the other side. Keep it honest with a contract test: a small check, run against the real service or its published schema, that fails when the stub and reality diverge. Without that, the stub will drift and the tests will pass while production fails.

## Keeping the suite healthy

- Keep the system under test small. Two components and one real dependency is usually enough; chain several small tests instead of building one large scenario.
- Share expensive setup, such as one container per test run, but never share data between tests.
- A flaky integration test is a defect. Fix the cause or delete the test; do not add retries to hide it.
- Every integration test has an owner through the repo's ownership mechanism, so a failure reaches someone.
- Keep the ratio sensible. Most behaviour belongs in unit tests; integration tests cover seams, not every branch.

## Do not

- Sleep for a fixed time to wait for something.
- Point tests at shared environments or real third-party production endpoints.
- Mock the very dependency the test is supposed to prove.
- Assert on log text or internal state when an observable result exists.
- Mark a flaky test as retry-until-green.
- Report success without running the test against real dependencies. If they cannot start here, say so and give the command.

## Report

State: the seam each test proves; which dependencies are real and which are stubbed, and how stubs are kept honest; the command run, how many consecutive runs passed, and the run time; anything not covered, and why.

Sources for these rules are in [references/sources.md](references/sources.md).
