# Coding standards: Kotlin

The project's own formatter and linter configuration comes first. Where the project has none, these defaults follow the Android Kotlin style guide and the Kotlin coding conventions.

## Find and run

Look in `build.gradle.kts`, `gradle/libs.versions.toml`, `.editorconfig` and `detekt.yml` for the tools and their settings. Use the Gradle wrapper.

| Job | Typical command |
| --- | --- |
| Format | `./gradlew ktlintFormat` or `./gradlew spotlessApply` |
| Lint | `./gradlew ktlintCheck`, `./gradlew detekt` |
| Compile | `./gradlew compileKotlin` |
| Everything wired in | `./gradlew check` |

Use only the plugins the build already declares. ktlint reads `.editorconfig`, so that file is often where the house style lives.

## Layout

- One theme per file. A file with a single top-level class is named after it; a file of several declarations gets a descriptive name.
- Order: licence header if used, file annotations, package, imports, declarations.
- No wildcard imports. One ASCII-sorted import list.
- Four-space indentation, no tabs. 100-column limit.
- Braces on `if`, `for`, `when` branches, `do` and `while`, except a one-line `if` with at most one `else`.
- No semicolons. One statement per line.
- Break before `.`, `?.` and `::`; break after binary operators.

Projects commonly differ on column limit (120) and on trailing commas. Follow the project.

## Naming

| Thing | Convention | Example |
| --- | --- | --- |
| Package | lowercase, no underscores | `com.example.billing` |
| Class, interface, object, type alias | PascalCase | `InvoiceRepository` |
| Function, property, parameter, local | camelCase | `findOverdueInvoices` |
| Constant (`const val`, or top-level or object `val` that is deeply immutable) | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Backing property | leading underscore | `_state` behind `state` |
| Type variable | single capital, or name ending in `T` | `T`, `RequestT` |
| Composable returning `Unit` | PascalCase noun | `InvoiceCard` |
| Test class | subject plus `Test` | `InvoiceRepositoryTest` |

Treat acronyms as words: `HttpClient`, `customerId`. No Hungarian prefixes.

## Language rules

- `val` over `var`. Read-only collection interfaces (`List`, `Map`) in signatures; mutable ones only where mutation is the contract.
- Model absence with nullable types and handle it with `?.`, `?:` and smart casts. Avoid `!!`; if a value truly cannot be null, restructure so the type says so, or use `requireNotNull(value) { "why" }`.
- `data class` for values, `sealed interface` for closed hierarchies, `enum class` for fixed sets, `object` for stateless singletons, `value class` for typed wrappers around a single value.
- `when` over sealed types and enums as an exhaustive expression, without an `else` branch, so the compiler flags a new variant.
- Expression-bodied functions for single expressions. Keep explicit return types on public API.
- Default and named arguments instead of overloads and builders. Name boolean and same-typed arguments at call sites.
- String templates instead of concatenation.
- Scope functions sparingly and one level deep: `let` for a nullable value, `apply` to configure an object, `also` for a side effect, `use` for closeables.
- Extension functions for genuinely reusable operations on a type you do not own; keep their visibility as narrow as possible.
- Top-level functions instead of utility classes.
- `internal` or `private` by default; make something public only when another module needs it.

## Coroutines

- Suspending functions are main-safe: a function that blocks switches dispatcher itself with `withContext`.
- Inject dispatchers; do not hard-code them.
- Launch work in a scope tied to a lifecycle. No `GlobalScope`.
- Never swallow `CancellationException`. If catching broadly, rethrow it.
- Expose `Flow` or `StateFlow` as read-only types; keep the mutable one private behind a backing property.

## Errors

- `require(condition) { "message" }` for arguments, `check(condition) { "message" }` for state, `error("message")` for unreachable branches.
- Throw specific exceptions and keep the cause when wrapping.
- No empty `catch`. No `catch (e: Throwable)`.
- Model expected failures in the return type (a sealed result type or nullable) when callers are meant to handle them; use exceptions for the unexpected.
- `use { }` for anything closeable.

## Documentation

- KDoc on every public type and public or protected member, unless it is self-explanatory or an override.
- Start with a summary fragment. Tags in order: `@param`, `@property`, `@return`, `@throws`, `@see`, with no empty descriptions.

## Java interop

When Java code calls this Kotlin: add `@JvmStatic`, `@JvmOverloads`, `@JvmField` or `@Throws` where the Java caller needs them, and avoid exposing Kotlin-only constructs in that API.

## Suppressions

Scope to the declaration, name the rule, and give the reason:

```kotlin
@Suppress("UNCHECKED_CAST") // Safe: the registry stores only values registered under this key's type.
```
