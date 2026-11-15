# Eval cases: design-patterns

Written cases, not yet an automated harness. Run each task with and without the skill and compare against the checklist.

## Trigger

Should invoke the skill:

1. "How should I structure the payment methods so adding one is easier?"
2. "Apply the strategy pattern here."
3. "This class has a 200-line switch statement. Refactor it."
4. "Is this abstraction worth having?"
5. "Design the classes for a notification module."

Should not invoke the skill:

1. "Should we split this into microservices?"
2. "Fix the bug in this method."
3. "Format this file." (coding-standards)
4. "Review my PR." (code-review)
5. "What is the observer pattern?" (a knowledge question, no code decision)

## Task 1: repeated conditional with a real force

Setup: three functions each switching on the same type code, with four variants, and a recent commit that updated two of the three.

Prompt: "Make it easier to add a new variant."

Pass when:

- [ ] The force is stated in one sentence with the locations.
- [ ] The simplest option (a lookup table) is considered before a class hierarchy.
- [ ] The chosen structure makes a missed variant a compile-time or test-time failure.
- [ ] Behaviour is unchanged, shown by tests run before and after.
- [ ] The report states the cost added.

## Task 2: untestable dependency

Setup: a service that constructs its own database client inside a method.

Prompt: "Improve the design of this class."

Pass when:

- [ ] The dependency is passed in.
- [ ] No interface is introduced unless a second implementation or a fake needs it.
- [ ] No container or framework is added.

## Negative task 1: pattern with no force

Setup: a module that constructs one type in one place with a plain constructor.

Prompt: "Add a factory and a builder for this so it's more extensible."

Pass when:

- [ ] The response checks for the force and finds none.
- [ ] It declines to add the patterns, says why, and names what would justify them later.
- [ ] If the user's stated reason reveals a real need, that need is addressed with the lightest structure.

## Negative task 2: similar but unrelated code

Setup: two functions with similar text that serve different business rules and have changed independently in git history.

Prompt: "Remove the duplication between these."

Pass when:

- [ ] The response notes they change for different reasons.
- [ ] It does not merge them behind a shared abstraction with mode flags, or does so only for the genuinely shared part.
