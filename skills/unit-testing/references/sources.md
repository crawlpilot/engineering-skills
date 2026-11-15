# Sources: unit-testing

| Rule in this skill | Source | How it was used |
| --- | --- | --- |
| Test through public APIs; test state, not interactions; prefer real objects over mocks when fast and deterministic | [Software Engineering at Google, ch. 12, Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html) | Read; paraphrased |
| A test changes only when required behaviour changes | Same chapter, "unchanging tests" | Read; paraphrased |
| One behaviour per test, named for the behaviour; no logic in tests; clear failure messages | Same chapter | Read; paraphrased |
| Descriptive over deduplicated; helpers with defaults and overrides; values a test depends on stay in the test | Same chapter, on DAMP and sharing code | Read; paraphrased |
| Roughly 80% unit tests, 20% broader | Same chapter | Read |
| Reviewers check that tests would fail when the code breaks and make useful assertions | [Google Engineering Practices: What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html) | Read; basis for "prove each test can fail" |
| Dependencies mocked in unit tests so error-handling edge cases can be exercised; builds without network | [Amazon Builders' Library: Automating safe, hands-off deployments](https://builder.aws.com/content/3ErTKQOTKc5NIw031UePBPxTQ6I/automating-safe-hands-off-deployments) | Read; basis for hermetic rule |

From general engineering knowledge, not a cited source: the case checklist (boundaries, invalid input, state), the "write the failing test first for a bug fix" step, the ordering of test doubles, and the language reference files. Tool names and flags in the reference files should be checked against the versions a project uses.
