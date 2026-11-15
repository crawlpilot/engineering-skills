# Eval cases: unit-testing

Written cases, not yet an automated harness. Run each task with and without the skill and compare against the checklist.

## Trigger

Should invoke the skill:

1. "Add tests for `PriceCalculator`."
2. "This function has no coverage, can you fix that?"
3. "I fixed the rounding bug in `invoice.py`. Write a regression test."
4. "Make `ReportGenerator` testable; it calls `datetime.now()` everywhere."
5. "Two tests in `OrderServiceTest` are failing after my change. Sort them out."

Should not invoke the skill:

1. "Test that our repository works against real Postgres." (integration-testing)
2. "Review this PR." (code-review)
3. "Write a load test for the checkout endpoint."
4. "Why is CI slow?"
5. "Explain what this test does."

## Task 1: untested function with an edge-case bug

Setup: a small module with a pure function, for example a tier lookup that uses `>` where `>=` is required at a boundary. A test framework is configured and one unrelated test file exists.

Prompt: "Add unit tests for this function."

Pass when:

- [ ] Existing test files were read and their style, framework and location matched.
- [ ] Tests cover typical input, both sides of every boundary, and invalid input.
- [ ] The boundary bug is found and reported, not silently encoded as expected behaviour.
- [ ] Each test checks one behaviour and is named for it.
- [ ] No logic, loops or recomputed expectations in the tests.
- [ ] The report says each new test was seen failing, and gives the command and result.

## Task 2: bug fix needing a regression test

Setup: a function with a reported bug and a failing scenario described in an issue.

Prompt: "Fix this bug."

Pass when:

- [ ] A test reproducing the bug was written and shown to fail before the fix.
- [ ] The fix is minimal and the new test passes.
- [ ] The whole suite was run, not only the new test.

## Task 3: code that is hard to test

Setup: a class that reads the system clock and constructs its own HTTP client inside a method.

Prompt: "Write unit tests for this class."

Pass when:

- [ ] The obstacle is named explicitly.
- [ ] The smallest seam is proposed (inject the clock and client) rather than patching internals broadly.
- [ ] No static or constructor mocking is introduced where a seam would do.
- [ ] What remains untested is stated.

## Negative task: pressure to go green

Setup: an existing test fails because the production code is wrong.

Prompt: "This test is failing, just make the build pass."

Pass when:

- [ ] The test is not deleted, skipped or weakened.
- [ ] The response says which side is wrong and why, and fixes the production code or asks before changing the expectation.
