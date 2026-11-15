# Sources: integration-testing

| Rule in this skill | Source | How it was used |
| --- | --- | --- |
| Larger tests exist for fidelity and to catch mock drift, configuration errors and emergent behaviour | [Software Engineering at Google, ch. 14, Larger Testing](https://abseil.io/resources/swe-book/html/ch14.html) | Read; paraphrased |
| Structure: system under test, seeded data, actions, verification | Same chapter | Read; paraphrased |
| Prefer hermetic systems under test over shared staging; keep the system under test small; chain small tests | Same chapter | Read; paraphrased |
| Contract tests keep doubles in step with the real service | Same chapter | Read; paraphrased |
| Every larger test has a documented owner | Same chapter | Read; paraphrased |
| Integration tests call real APIs on real infrastructure and cover positive and negative cases and full workflows | [Amazon Builders' Library: Automating safe, hands-off deployments](https://builder.aws.com/content/3ErTKQOTKc5NIw031UePBPxTQ6I/automating-safe-hands-off-deployments) | Read; paraphrased |
| Old and new versions run side by side during rollout, so compatibility in both directions is tested | Same article, on one-box and backward compatibility | Read; basis for the compatibility case |
| Most tests should be unit tests | [Software Engineering at Google, ch. 12](https://abseil.io/resources/swe-book/html/ch12.html) | Read |

From general engineering knowledge, not a cited source: wait-on-condition instead of sleeping, the three-consecutive-runs check, the case checklist details, network-level stubbing, and the language reference files. Library names and APIs in the reference files should be checked against the versions a project uses. Of the examples, only `vi.waitFor` was executed (under Vitest 5.1); the Testcontainers, MSW, WireMock, Ktor and Awaitility examples were syntax-checked where possible but not run against real containers or services.
