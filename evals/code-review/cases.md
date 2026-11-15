# Eval cases: code-review

Written cases, not yet an automated harness. Run each task with and without the skill and compare against the checklist.

## Trigger

Should invoke the skill:

1. "Review this PR."
2. "Can you look over my branch before I merge?"
3. "Is this change safe to ship?"
4. "Give me feedback on this diff."
5. "Check what the agent just changed."

Should not invoke the skill:

1. "Fix the bug in `checkout.py`."
2. "Write tests for this." (unit-testing)
3. "Explain how this module works."
4. "Do a penetration test of the API."
5. "Refactor this class." (design-patterns or coding-standards)

## Task 1: diff with a planted defect

Setup: a 150-line change adding a feature, with one real bug (for example an off-by-one in pagination), one missing test for the new branch, and two style nits.

Prompt: "Review this change."

Pass when:

- [ ] The bug is found, classified as blocking, and shown with a failing input.
- [ ] The missing test is reported.
- [ ] Nits are labelled as nits and do not drive the verdict.
- [ ] The verdict is stated first, with its reason.
- [ ] Commands run and their results are listed.
- [ ] No invented findings.

## Task 2: wrong design, tidy code

Setup: a clean, well-tested change that puts business logic in the wrong layer, duplicating a rule that exists elsewhere.

Prompt: "Review this change."

Pass when:

- [ ] The design problem is raised before any line-level comment.
- [ ] The review does not bury it under minor points.

## Task 3: change that cannot be rolled back

Setup: a change that drops a database column in the same release that stops writing it.

Prompt: "Review this change."

Pass when:

- [ ] The rollback and mixed-version risk is identified as blocking.
- [ ] A staged alternative is suggested.

## Task 4: oversized mixed change

Setup: a 1,500-line change mixing a rename across many files with a behaviour change.

Prompt: "Review this change."

Pass when:

- [ ] The review says the change should be split, and how.
- [ ] It states which parts were and were not reviewed.

## Negative task: a good change

Setup: a small, correct, well-tested change.

Prompt: "Review this change."

Pass when:

- [ ] The review approves briefly.
- [ ] No findings are manufactured to appear thorough.
