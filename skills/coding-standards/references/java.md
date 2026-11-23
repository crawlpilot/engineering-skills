# Coding standards: Java

The project's own formatter and linter configuration comes first. Where the project has none, these defaults follow the Google Java Style Guide.

## Find and run

| Job | Maven | Gradle |
| --- | --- | --- |
| Format | `mvn spotless:apply` or `mvn fmt:format` | `./gradlew spotlessApply` |
| Check format and lint | `mvn verify` | `./gradlew check` |
| Compile only | `mvn -q compile` | `./gradlew compileJava` |
| Tests | `mvn test` | `./gradlew test` |

Use only the plugins the build already declares. Look in `pom.xml` or `build.gradle(.kts)` for Spotless, google-java-format, Checkstyle, Error Prone, SpotBugs or PMD, and for a Checkstyle or EditorConfig file that defines the house style.

## Layout

- One top-level class per file. Order: licence header if used, package, imports, class.
- No wildcard imports. Static imports in one block, then non-static, each in ASCII order.
- Two-space indentation, no tabs. 100-column limit.
- Braces on every `if`, `else`, `for`, `do` and `while`, even for a single statement. Opening brace on the same line.
- One statement per line.

Projects commonly differ on indentation (four spaces) and column limit (120). Follow the project.

## Naming

| Thing | Convention | Example |
| --- | --- | --- |
| Package | lowercase, no underscores | `com.example.billing` |
| Class, interface, record, enum | UpperCamelCase noun | `InvoiceRepository` |
| Method | lowerCamelCase verb | `findOverdueInvoices` |
| Constant (`static final`, deeply immutable) | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Field, parameter, local | lowerCamelCase | `retryCount` |
| Type variable | single capital or capital plus `T` | `T`, `RequestT` |
| Test class | subject plus `Test` | `InvoiceRepositoryTest` |

No Hungarian prefixes or suffixes (`mName`, `name_`). Avoid one-character parameter names in public methods.

## Language rules

- `@Override` wherever it is legal.
- Never ignore a caught exception. If doing nothing is correct, say why in a comment.
- Qualify static members with the class name, not an instance.
- Every `switch` is exhaustive. Old-style fall-through is marked with a comment.
- Javadoc on every public class and every public or protected member, unless it is self-explanatory or overrides a supertype method. Start with a summary fragment.

## Idioms for modern Java

Use what the project's language level allows; check the compiler `release` or `source` setting first.

- `record` for immutable data carriers instead of hand-written getters, `equals` and `hashCode`.
- `sealed` interfaces with pattern-matching `switch` for closed sets of variants.
- `var` for locals only when the type is obvious from the right-hand side.
- `Optional` as a return type for "may be absent". Not for fields, parameters or collections; return an empty collection instead.
- `List.of`, `Map.of` and `Collectors.toUnmodifiableList` for immutable collections. Do not return internal mutable collections.
- try-with-resources for anything `AutoCloseable`.
- `java.time` types. Take a `Clock` where the current time matters.
- `final` fields by default; constructor injection for dependencies.
- Streams for simple transformations; a plain loop when the stream needs side effects or becomes hard to read.
- Text blocks for multi-line strings.

## Errors

- Throw the most specific exception that fits. `IllegalArgumentException` for bad arguments, `IllegalStateException` for bad state.
- Validate arguments at public entry points: `Objects.requireNonNull(order, "order")`.
- Wrap with context and keep the cause: `throw new InvoiceLoadException("invoice " + id, e);`
- Do not use exceptions for ordinary control flow.
- Restore the interrupt flag when catching `InterruptedException`.

## Logging

- Use the project's logging facade with parameterised messages: `log.info("Invoice {} sent", id);` not string concatenation.
- Never log secrets, tokens or personal data.
- Log an exception once, where it is handled, with the exception as the last argument.

## Suppressions

When a rule must be suppressed, scope it as narrowly as possible and say why:

```java
@SuppressWarnings("unchecked") // Safe: the map is populated only by register(), which enforces the type.
<T> Handler<T> handlerFor(Class<T> type) {
  return (Handler<T>) handlers.get(type);
}
```
