# Sources: coding-standards

| Rule in this skill | Source | How it was used |
| --- | --- | --- |
| The style guide is the authority; where it is silent, match surrounding code; keep large reformatting in its own change | [Google Engineering Practices: What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html) | Read; paraphrased |
| Comments explain why; simplify unclear code instead of explaining it; remove stale TODOs | Same page | Read; paraphrased |
| No generality or features the system does not need yet | Same page, on complexity | Read; paraphrased |
| Java layout, imports, braces, indentation, column limit, naming, `@Override`, caught exceptions, static qualification, exhaustive switches, Javadoc | [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html) | Read; summarised in `java.md` |
| Python imports, exceptions, mutable global state, comprehensions, default arguments, properties, truth-value tests, type annotations, line length, indentation, docstrings, string formatting, naming, main guard, function length | [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) | Read (first 100,000 of about 103,000 characters); summarised in `python.md` |
| Kotlin file structure, imports, braces, indentation, column limit, expression functions, implicit types, naming (including backing properties, type variables, acronyms, composables), test naming, KDoc | [Android Kotlin style guide](https://developer.android.com/kotlin/style-guide) | Read; summarised in `kotlin.md` |
| TypeScript imports and exports, variable declarations, naming, classes, functions, equality, assertions, `unknown`, interfaces and type aliases, enums, array types, null and undefined, exceptions, iteration, switch | [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html) | Read (first 100,000 of about 122,000 characters; the `any` and `@ts-ignore` sections were not in the part read); summarised in `javascript-typescript.md` |
| Kotlin coding conventions (JetBrains) | Kotlin documentation | From general knowledge; the page was not read for this repository |
| PEP 8 line length of 79 and general Python layout conventions | PEP 8 | From general knowledge; the page was not read for this repository |

From general engineering knowledge, not a cited source: the workflow (smallest change, match the file, reread your own diff), the modern-Java, Kotlin, Python typing and TypeScript idiom lists beyond what the style guides state (including the coroutine rules, the `any` and `@ts-expect-error` guidance, and the discriminated-union example), logging guidance, and the tool names and commands in the reference files. Check tool commands against the versions a project uses; Black's default line length of 88 is stated from general knowledge.
