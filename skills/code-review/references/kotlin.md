# Code review: Kotlin

Language-specific things to look for, after the general checklist. Each is a prompt to check, not an automatic finding: confirm it applies before reporting it.

## Verify, if the tools are present

```bash
./gradlew check          # compiles, tests, and runs whatever static analysis is wired in
./gradlew detekt         # if the project uses detekt
./gradlew ktlintCheck    # if the project uses ktlint
```

Note which checks the build already enforces so the review does not repeat them.

## Null safety

- `!!` anywhere outside tests. Ask what guarantees non-null; expect `?:`, `requireNotNull` with a message, or a restructured type.
- Platform types from Java (`String!`) flowing into non-null Kotlin types without a check.
- `lateinit var` where a constructor parameter, `by lazy` or a nullable type would be safer; reads before initialisation.
- Unsafe casts with `as` where `as?` and handling the null was intended.
- `?.let { }` chains that silently skip work when a value is unexpectedly null.

## Correctness

- **Equality.** `===` used where structural `==` was meant. A data class containing an array or mutable collection, which breaks `equals` and `hashCode`.
- **Data classes.** Mutable `var` properties in a data class used as a map key or in a set. `copy()` bypassing validation done in a factory.
- **When.** A `when` over a sealed type or enum used as a statement with an `else` branch that would hide a newly added variant. Prefer exhaustive `when` without `else`.
- **Collections.** A read-only `List` interface that is backed by a mutable list still shared with a writer. `first()`, `single()` or `[index]` on a collection that can be empty.
- **Numbers and time.** `Double` for money; integer overflow; `LocalDateTime` where an instant is needed.
- **Scope functions.** Nested `let`, `run`, `apply`, `also` where `it` and `this` become ambiguous; `apply` used for side effects unrelated to the receiver.
- **Default arguments.** A default value evaluated at each call that performs I/O or reads the clock.

## Coroutines

- `GlobalScope.launch`, or a scope created and never cancelled. Expect structured concurrency: work launched in a scope tied to a lifecycle.
- `runBlocking` in production code paths, especially on a request or UI thread.
- Blocking calls (JDBC, file I/O, `Thread.sleep`) inside a suspending function without switching to an appropriate dispatcher.
- Hard-coded `Dispatchers.IO` or `Dispatchers.Main` instead of an injected dispatcher.
- `catch (e: Exception)` or `runCatching` around suspending code that swallows `CancellationException`. Cancellation must be rethrown.
- `async` without `await`, or `launch` whose failure nobody observes.
- Shared mutable state accessed from several coroutines without a `Mutex`, an atomic or confinement to one dispatcher.
- `Flow`: collection in the wrong scope; `stateIn` or `shareIn` without a sensible start strategy; side effects in operators that should be in `onEach` or the collector.
- A suspending call that needs a timeout and has none.

## Errors and resources

- Empty `catch` blocks; `catch (e: Throwable)`.
- `runCatching { }` followed by `getOrNull()` that discards the failure without logging or handling.
- Closeable resources not wrapped in `use { }`.
- Exceptions wrapped without passing the cause.
- `require` and `check` used correctly: `require` for arguments, `check` for state, both with a message.

## API and design

- Public API with inferred return types in a library module; expect explicit types.
- `open` classes or functions with no subclass; classes that should be `internal` or `private`.
- A class hierarchy that should be a `sealed interface`; a class with only data that should be a `data class`; a wrapper that should be a `value class`.
- Extension functions on very general types (`Any`, `String`) polluting the namespace.
- A single-method interface that should be a `fun interface` or a function type.
- An `object` singleton holding mutable state.
- Boolean parameters at call sites without named arguments.

## Java interop

- Missing `@JvmStatic`, `@JvmOverloads` or `@Throws` where Java callers need them.
- Kotlin code calling Java methods that return null without annotations.
- SAM conversions that capture more than intended.

## Security prompts

Flag and recommend specialist review; do not treat this list as an audit.

- SQL built with string templates instead of bound parameters.
- Secrets, tokens or personal data in logs, exception messages or a data class's generated `toString()`.
- Deserialising untrusted input with polymorphic configuration left open.
- On Android: exported components without permission checks, sensitive data in shared preferences or logs, WebView with JavaScript enabled on untrusted content, cleartext traffic.

## Framework prompts (when present)

- Spring: `@Transactional` on a function called from within the same class; final classes without the `all-open` plugin configured; a transaction spanning a suspending remote call.
- Android and Compose: work launched outside a lifecycle-aware scope; state read in a way that triggers excess recomposition; a `ViewModel` holding a reference to a view or activity context.
- Ktor: blocking calls inside route handlers; missing content-negotiation or validation on input.

## Tests in the change

- `runBlocking` with real delays instead of `runTest`.
- Fully relaxed mocks; mocks of data classes or sealed types.
- `!!` where an assertion would give a clearer failure.
- Shared mutable state in a `companion object`.
