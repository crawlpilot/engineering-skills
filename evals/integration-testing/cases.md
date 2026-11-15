# Eval cases: integration-testing

Written cases, not yet an automated harness. Run each task with and without the skill and compare against the checklist.

## Trigger

Should invoke the skill:

1. "Write integration tests for `OrderRepository` against Postgres."
2. "Add API tests for the `/orders` endpoints."
3. "Our unit tests pass but the service fails when it talks to the payment API. Add tests that would catch that."
4. "I changed the Kafka consumer config. How do we test it?"
5. "Add a contract test for our client of the inventory service."

Should not invoke the skill:

1. "Add unit tests for this pure function." (unit-testing)
2. "Set up a load test."
3. "Review the test coverage report."
4. "Write a Dockerfile for the service."
5. "Mock the database in this unit test."

## Task 1: repository against a real database

Setup: a repository class with save and find methods, migrations in the repo, a container runtime available.

Prompt: "Add integration tests for this repository."

Pass when:

- [ ] The seam is stated.
- [ ] The production database engine runs in a container; no in-memory substitute.
- [ ] The project's real migrations build the schema.
- [ ] Each test seeds and isolates its own data.
- [ ] Cases include success, not-found and a constraint violation.
- [ ] Tests are tagged or placed so they run in the integration stage.
- [ ] The report gives the number of consecutive passing runs and the run time.

## Task 2: HTTP client against a third-party API

Setup: a client class calling an external payment API that cannot be reached from tests.

Prompt: "Test this client."

Pass when:

- [ ] The stub sits at the network level, not inside the client.
- [ ] Failure modes are covered: error status, timeout, connection failure, malformed body.
- [ ] The response says how the stub is kept honest, or flags that no contract check exists.
- [ ] No fixed sleeps.

## Task 3: asynchronous effect

Setup: an action that publishes a message consumed asynchronously.

Prompt: "Add a test that the event gets published."

Pass when:

- [ ] The test waits on a condition with a timeout.
- [ ] Identifiers are unique per test so parallel runs do not collide.

## Negative task: flaky test

Setup: an integration test that fails intermittently because of a fixed sleep.

Prompt: "This test is flaky, add a retry."

Pass when:

- [ ] No retry-until-green is added.
- [ ] The cause is identified and fixed, or the limitation is reported with the reason.
