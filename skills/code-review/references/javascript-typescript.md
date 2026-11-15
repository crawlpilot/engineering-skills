# Code review: JavaScript and TypeScript

Language-specific things to look for, after the general checklist. Each is a prompt to check, not an automatic finding: confirm it applies before reporting it.

## Verify, if the tools are present

Use the project's scripts from `package.json` and its package manager. Typical ones:

```bash
npm run lint          # usually ESLint
npm run typecheck     # or: npx tsc --noEmit
npm test
npx prettier --check .
```

Do not report as findings things the configured linter, formatter or compiler already enforces.

## Async and promises

- A promise that is neither awaited, returned nor explicitly handled. Errors vanish and ordering becomes accidental.
- `await` inside a loop where the calls are independent and should run together, or `Promise.all` where a single failure should not discard the other results (`Promise.allSettled`).
- An `async` function passed where a synchronous callback is expected, such as `forEach` or an event emitter listener; rejections are unhandled.
- Missing `try`/`catch` or `.catch` at the boundary where an async failure should be handled.
- No timeout or abort signal on network calls. `fetch` has no default timeout.
- Shared state mutated across `await` points, assuming nothing else ran in between.
- Blocking the event loop in a server: synchronous file or crypto calls, large JSON parsing, tight CPU loops.

## Correctness

- **Equality.** `==` or `!=` other than a deliberate `== null` check.
- **Truthiness.** `if (value)` or `value || fallback` where `0`, `''` or `false` is valid. Expect `??` and explicit comparisons.
- **Optional chaining.** `a?.b.c` that still throws when `b` is undefined; chains that silently skip required work.
- **Mutation.** Mutating function arguments, props or shared state; `sort()` and `reverse()` mutating in place.
- **Numbers.** Floats for money; `parseInt` without a radix or on untrusted input without a NaN check; integers beyond the safe range.
- **Dates.** Parsing non-ISO date strings; local-time methods where UTC is intended; month indices starting at zero.
- **Iteration.** `for...in` over an array; mutating a collection while iterating it.
- **Closures.** Stale values captured in callbacks, timers and effect hooks.
- **Equality of objects.** Comparing objects or arrays with `===` expecting structural equality.

## TypeScript

- `any`, explicit or implicit, especially on data crossing a boundary. Expect `unknown` plus narrowing or validation.
- Type assertions (`as Foo`) and non-null assertions (`!`) without a comment explaining why they are safe.
- `@ts-ignore` or `@ts-expect-error` without a reason.
- External data (HTTP responses, `JSON.parse`, environment variables, form input) typed by assertion instead of validated at runtime.
- Unions handled by a `switch` without an exhaustiveness check, so a new member is silently ignored.
- Optional properties used where the value is in fact required.
- Types widened to make an error go away (`string` instead of a literal union, `object`, `Function`).
- Exported functions without explicit return types where the project requires them.
- Enum misuse: numeric enums accepting any number; truthiness checks on an enum whose first value is zero.

## Errors and resources

- Empty `catch` blocks, or `catch` that logs and continues as if nothing happened.
- Throwing strings or plain objects instead of `Error` instances; errors rethrown without `cause`.
- A `catch` variable used as if it were known to be an `Error` where arbitrary values can be thrown.
- Event listeners, timers, subscriptions, streams or database connections that are never removed or closed.
- A `try` block wrapping far more than the call that can fail.

## Modules and dependencies

- A new dependency for something small or already available in the platform or an existing dependency.
- A dependency added to `dependencies` that belongs in `devDependencies`, or the reverse.
- Lockfile changes that do not match the manifest change, or a second lockfile from a different package manager.
- Default exports in a codebase that uses named exports; circular imports; deep imports into another package's internals.
- Server-only code or secrets imported into a client bundle.

## Security prompts

Flag and recommend specialist review; do not treat this list as an audit.

- Untrusted content written with `innerHTML`, `dangerouslySetInnerHTML`, `document.write` or an unescaped template.
- SQL or shell commands built by string concatenation; `child_process.exec` with interpolated input.
- `eval`, `new Function`, or dynamic `require`/`import` with user-controlled input.
- Object merging or property assignment from untrusted keys (`__proto__`, `constructor`) that enables prototype pollution.
- File paths built from user input without resolving against a base directory.
- Secrets in source, client bundles, logs or error responses; tokens stored where scripts can read them.
- Regular expressions with nested quantifiers applied to untrusted input.
- Open redirects from a user-supplied URL; overly permissive CORS; missing authorisation checks on a new route.
- `Math.random` used for tokens or identifiers that must be unguessable.

## Framework prompts (when present)

- React: missing or incorrect hook dependency arrays; state mutated in place; effects without cleanup; index used as a key for reorderable lists; derived state stored instead of computed.
- Next.js and similar: data fetching on the wrong side of the server and client boundary; server secrets reachable from client components.
- Express and Fastify: async handlers whose rejections are not forwarded to the error handler; missing input validation; no body size limits.
- ORMs: a query inside a loop; raw queries with interpolation; missing transactions around multi-step writes.

## Tests in the change

- A missing `await` on an async assertion.
- `it.only`, `describe.only`, `it.skip` or `xit` left in.
- Snapshot updates accepted without reading the diff.
- Module mocks of third-party internals; mocks never reset between tests.
- Fixed sleeps instead of waiting on a condition.
