# Code review: Java

Language-specific things to look for, after the general checklist. Each is a prompt to check, not an automatic finding: confirm it applies before reporting it.

## Verify, if the tools are present

```bash
mvn -q verify            # or: ./gradlew check
git diff --stat <base>...HEAD
```

Note which static analysis the build already runs (Error Prone, Checkstyle, SpotBugs, PMD, NullAway) so the review does not repeat what the build enforces.

## Correctness

- **Nulls.** A new method that can return null without saying so; a dereference of a value that can be null; `Optional` used as a field or parameter, or `Optional.get()` without a presence check.
- **Equality.** `==` on strings or boxed numbers; `equals` overridden without `hashCode`; a mutable object used as a map key.
- **Numbers.** `double` or `float` for money (expect `BigDecimal` or integer minor units); integer overflow in size or time arithmetic; integer division where a fraction was intended.
- **Time.** `Date`, `Calendar` or `LocalDateTime` where an instant or zoned time is needed; `Instant.now()` or `System.currentTimeMillis()` inline in logic that should take a `Clock`.
- **Collections.** Modifying a collection while iterating it; returning an internal mutable collection; assuming iteration order from a `HashMap` or `HashSet`.
- **Streams.** Side effects inside `map` or `filter`; a stream consumed twice; `parallelStream()` on shared mutable state or blocking calls.
- **Switch.** Fall-through without a marker in old-style switches; a missing `default` or a non-exhaustive switch over an enum or sealed type.

## Resources and errors

- Anything `Closeable` (streams, connections, HTTP responses, locks) opened without try-with-resources.
- A `catch` that swallows, or logs and continues as if nothing happened. An empty catch needs a comment explaining why.
- Catching `Exception` or `Throwable` where a specific type is meant; catching `InterruptedException` without restoring the interrupt flag.
- Exceptions rethrown without the cause attached.
- `finally` blocks that return or throw, masking the original error.

## Concurrency

- Shared mutable state without synchronisation; a non-thread-safe type (`HashMap`, `ArrayList`, `SimpleDateFormat`) reachable from several threads.
- Check-then-act on a concurrent collection (`if (!map.containsKey(k)) map.put(k, v)`) instead of an atomic method.
- Blocking calls on a shared or common pool; unbounded executors or queues; missing timeouts on futures and network calls.
- Locks acquired in inconsistent order; lock not released in `finally`.
- Fields read by other threads that are neither `final`, `volatile` nor guarded.

## API and design

- New public surface that could be package-private. Mutable public fields.
- A class that could be a `record`; a closed hierarchy that could be `sealed`.
- An interface with a single implementation and no test double; a factory that builds one type.
- Inheritance used to share code where composition would do.
- A change to a public method signature, serialised form or database mapping without a compatibility plan.

## Security prompts

Flag and recommend specialist review; do not treat this list as an audit.

- SQL built by string concatenation instead of bound parameters.
- Deserialising untrusted data with native Java serialisation or a polymorphic JSON configuration.
- Secrets, tokens or personal data written to logs or exception messages.
- File paths built from user input without normalisation and a base-directory check.
- `Random` used where `SecureRandom` is required; hand-rolled cryptography.
- TLS verification or hostname checks disabled.

## Framework prompts (when present)

- Spring: `@Transactional` on a private method or called from within the same class; a transaction held across a remote call; field injection where constructor injection is the project's norm.
- JPA: lazy associations accessed outside a transaction; a query inside a loop; `equals` and `hashCode` based on a generated id.

## Tests in the change

- Test names that do not describe a behaviour; assertions on `toString()`.
- Mocks of value types or of the class under test; `verify` on every interaction.
- `Thread.sleep` in tests; shared static state between tests.
