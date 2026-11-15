---
name: design-patterns
description: Decide how to structure code and whether a design pattern is warranted. Use when asked to design a module or class structure, apply or pick a pattern, refactor toward better structure, remove duplication or growing conditionals, or review whether an abstraction is justified. Covers naming the problem first, the simplest structure that solves it, and refusing patterns nothing needs yet. Not for system-level architecture or service boundaries.
---

# Design patterns

A pattern is a named solution to a recurring problem. It is justified by the problem being present in the code today, not by the pattern being familiar. Most of this skill is deciding whether one is needed at all.

## Read first

1. Read the code involved and its callers. Count how many variants, call sites or implementations actually exist now.
2. Look for how the codebase already solves similar problems, and which patterns and frameworks it already uses. A dependency-injection container, for example, already supplies several patterns.
3. Open the reference for the language in use: [Java](references/java.md), [Kotlin](references/kotlin.md), [Python](references/python.md) or [JavaScript and TypeScript](references/javascript-typescript.md). Many classic patterns are a language feature in modern languages.

## Workflow

1. **Name the force, in the code's own terms.** Write one sentence about what is hard today: "adding a payment method means editing four switch statements", "this class cannot be tested without a live queue". If you cannot write that sentence with evidence from the code, stop: no pattern is needed.
2. **Try the simplest fix first.** A function, a parameter, a small data type, or deleting code. If that resolves the force, use it.
3. **If structure is needed, choose from the table below** by matching the force, not the pattern name.
4. **Check the cost.** Each pattern adds indirection: more types, more files, a longer path to follow when reading or debugging. State what is gained and what it costs.
5. **Apply it in the language's idiom**, using the reference file. Prefer the lightest form: a function over a single-method interface, a module over a singleton class.
6. **Keep behaviour identical when refactoring.** Make sure tests cover the existing behaviour before restructuring, move in small steps, and run tests after each.
7. **Report** as described at the end.

## Matching forces to structures

| Force observed in the code | Simplest thing to try | Pattern, if that is not enough |
| --- | --- | --- |
| Same conditional on a type or mode repeated in several places | One lookup table or map from key to function | Strategy; polymorphism over a sealed type |
| Behaviour must vary per caller and is chosen at runtime | Pass a function | Strategy |
| Object needs many optional settings; constructors are unreadable | Named or keyword arguments, a config data type | Builder |
| Creation logic is duplicated or depends on input | One factory function | Factory method; abstract factory only for families of related types |
| Need to add behaviour around an operation: logging, caching, retries | A wrapper function or decorator | Decorator; proxy |
| A third-party interface does not match what the code needs | A thin wrapper function | Adapter |
| A complex subsystem is used the same way in many places | A helper function | Facade |
| Many parts must react when something changes | A direct call, if there is one listener | Observer; event bus only for genuinely decoupled parts |
| Algorithm skeleton is fixed but steps vary | Pass the varying steps as functions | Template method |
| Behaviour depends on a state with defined transitions | An enum and one transition table | State |
| An operation must be queued, logged or undone | A function plus its arguments | Command |
| Code is untestable because it constructs its own dependencies | Pass the dependency in | Dependency injection |
| Data access is tangled with business logic | Move queries into functions in one module | Repository |

## The rule of three

Do not abstract on the first occurrence. On the second, note the duplication. On the third, abstract, and only if all three are the same concept and not merely similar text. Two things that look alike but change for different reasons should stay separate.

## Warning signs of a pattern that should not be there

- An interface with exactly one implementation and no test double that needs it.
- A factory that constructs one type.
- A class whose name ends in Manager, Helper or Processor and whose job cannot be stated in a sentence.
- A layer that only forwards calls.
- Configuration or extension points with no second user.
- Inheritance used to share code where composition or a plain function would do.
- A reader has to open more than three files to follow one operation.

When these appear in existing code, the right design work is often removal.

## Do not

- Introduce a pattern for a need that might arise later. Solve the future problem when it arrives and its shape is known.
- Apply a pattern because it was named in the request without checking that its force is present. If it is not, say so and propose the simpler structure.
- Restructure and change behaviour in the same step.
- Add a framework or library to obtain a pattern the language already provides.
- Rename existing concepts to pattern vocabulary when the codebase has its own terms.
- Call a design finished without the tests passing.

## Report

State: the force, in one sentence, with where it appears; what was chosen and the simpler options considered and why they were or were not enough; the cost added in types, files or indirection; that behaviour is unchanged, with the test command and result; anything deliberately not abstracted, and why.

Sources for these rules are in [references/sources.md](references/sources.md).
