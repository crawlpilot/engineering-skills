# Sources: design-patterns

This skill has the thinnest published backing of the six. The companies surveyed publish little on design patterns as such; what they do publish is guidance against unnecessary complexity, which is the core of this skill.

| Rule in this skill | Source | How it was used |
| --- | --- | --- |
| Flag over-engineering: generality or features the system does not need yet; solve the future problem when it arrives | [Google Engineering Practices: What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), on complexity | Read; paraphrased |
| Design is reviewed first: do the pieces interact sensibly and belong here | Same page, on design | Read; paraphrased |
| Do not accept changes that degrade code health; complexity accumulates through small additions | Same page | Read; paraphrased |
| State the trade-offs behind a design choice and the alternatives considered | [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/) | Read; basis for the report format |
| Prefer real objects and state-based tests, which favours injected dependencies over hidden ones | [Software Engineering at Google, ch. 12](https://abseil.io/resources/swe-book/html/ch12.html) | Read; basis for the dependency-injection rows |

From general engineering knowledge, not a cited source:

- The pattern vocabulary and the force-to-pattern table. The pattern names originate in *Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma, Helm, Johnson, Vlissides, 1994), which was not re-read for this repository.
- The rule of three, commonly attributed to Martin Fowler's *Refactoring*; also not re-read.
- The warning-sign lists and all language idioms and code in the reference files.

Before relying on this skill for a contested design decision, treat its table as a prompt for thinking and not as an authority.
