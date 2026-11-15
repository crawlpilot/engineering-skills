# Eval cases: coding-standards

Written cases, not yet an automated harness. Run each task with and without the skill and compare against the checklist.

## Trigger

Should invoke the skill:

1. "Add a `cancel` method to `OrderService`."
2. "Fix the null pointer in `InvoiceMapper`."
3. "Clean up this file so it passes lint."
4. "Make this function more idiomatic."
5. "Implement the retry logic described in the ticket."

Should not invoke the skill:

1. "Should this be a strategy or a state machine?" (design-patterns)
2. "Review my PR." (code-review)
3. "Write tests for this." (unit-testing)
4. "Explain what a decorator is."
5. "Upgrade the vulnerable dependency." (sca-fixes)

## Task 1: change in a repo with its own conventions

Setup: a repository whose formatter is configured to a non-default line length and whose code uses a specific error-handling and logging pattern.

Prompt: "Add input validation to this endpoint."

Pass when:

- [ ] Project configuration was read before writing.
- [ ] New code matches the file's existing error and logging patterns.
- [ ] The diff touches only what the change needs; no unrelated reformatting.
- [ ] Formatter, linter, type checker and tests were run, and results reported.

## Task 2: convention conflict

Setup: the project's configured style differs from the language's published guide on line length and quote style.

Prompt: "Add a helper function here."

Pass when:

- [ ] The project's configuration is followed.
- [ ] The conflict is not "fixed" by restyling existing code.

## Task 3: error handling

Setup: a function that calls an external service and currently swallows all exceptions.

Prompt: "This silently fails sometimes. Fix it."

Pass when:

- [ ] The broad catch is replaced by a narrow one or removed.
- [ ] The error carries context and keeps its cause.
- [ ] No empty handler remains without a stated reason.

## Negative task: lint pressure

Setup: a real type error flagged by the type checker.

Prompt: "The type checker is complaining, just make it stop."

Pass when:

- [ ] The underlying error is fixed rather than suppressed.
- [ ] If a suppression is truly needed, it is scoped to the line and carries a reason.
