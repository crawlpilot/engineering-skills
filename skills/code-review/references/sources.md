# Sources: code-review

| Rule in this skill | Source | How it was used |
| --- | --- | --- |
| The twelve review dimensions and their order: design, functionality, complexity, tests, naming, comments, style, consistency, documentation, every line, context, good things | [Google Engineering Practices: What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html) | Read; paraphrased and reordered into a checklist |
| Over-engineering is a complexity finding; solve present needs | Same page | Read; paraphrased |
| Tests belong in the same change; they should fail when the code breaks | Same page | Read; paraphrased |
| Style guide is the authority; mark optional points as "Nit:" and do not block on preference | Same page | Read; paraphrased |
| State which parts were not reviewed; bring in a qualified reviewer for security or privacy | Same page | Read; paraphrased |
| Approve when the change improves overall code health, even if not perfect | Google Engineering Practices, The Standard of Code Review | Seen in secondary summaries only; the page itself was not read |
| Review design before details; ask for a split when a change is too large | [Google Engineering Practices: Navigating a CL in review](https://google.github.io/eng-practices/review/reviewer/navigate.html) | Search excerpt only |
| Deployment-safety questions: tests, monitoring coverage, alarms, dependencies already deployed, clean rollback | [Amazon Builders' Library: Automating safe, hands-off deployments](https://builder.aws.com/content/3ErTKQOTKc5NIw031UePBPxTQ6I/automating-safe-hands-off-deployments), sample review checklist | Read; paraphrased |
| Speed must not come at the cost of time spent actually reading the change | [Meta Engineering: Improving code review time](https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving/) | Read; basis for "do not approve what you have not read" |

From general engineering knowledge, not a cited source: the four severity levels, the guidance on writing findings, and the Java and Python prompt lists in the reference files. The security prompts are common review heuristics, not a complete or authoritative checklist.
