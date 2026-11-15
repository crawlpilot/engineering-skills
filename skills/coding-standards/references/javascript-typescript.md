# Coding standards: JavaScript and TypeScript

The project's own ESLint, Prettier, TypeScript and editor configuration comes first. Where the project has none, these defaults follow the Google TypeScript Style Guide.

## Find and run

Read `package.json` scripts, the ESLint config (`eslint.config.*` or `.eslintrc*`), the Prettier config, `tsconfig.json` and `.editorconfig`. Use the project's package manager, shown by its lockfile.

| Job | Typical command |
| --- | --- |
| Format | `npx prettier --write <files>` |
| Lint | `npx eslint <files>` |
| Type check | `npx tsc --noEmit` |
| Tests | `npm test` |

Prefer the project's scripts (`npm run lint`, `npm run typecheck`) when they exist. Some projects use Biome or another tool in place of ESLint and Prettier; use what is configured and do not add a second one.

## Layout

Formatting is the formatter's job. Do not hand-format against it or argue with its output. Quote style, semicolons, trailing commas and line width come from its config.

## Modules

- ES module syntax. No `require` in TypeScript, no `namespace`.
- Named exports, not default exports, unless the project or a framework convention requires a default.
- `import type` for symbols used only as types.
- No mutable exports. Expose state through functions.
- Follow the project's import ordering and path alias conventions.

## Naming

| Thing | Convention | Example |
| --- | --- | --- |
| Variable, parameter, function, method, property | lowerCamelCase | `findOverdueInvoices` |
| Class, interface, type alias, enum, type parameter | UpperCamelCase | `InvoiceRepository` |
| Global constant, enum value | CONSTANT_CASE | `MAX_RETRIES` |
| File | whatever the project uses consistently | `invoice-repository.ts` |

No `I` prefix on interfaces, no `_` prefix for private members, no Hungarian notation. Treat acronyms as words: `loadHttpUrl`. A leading underscore is only for a required but unused parameter.

## Language rules

- `const` by default, `let` only when reassigned, never `var`. One declaration per statement.
- `===` and `!==`. The one accepted exception is `== null` to cover both null and undefined.
- `??` and `?.` for null and undefined. Do not use `||` for defaults when `0`, `''` or `false` are valid values.
- Function declarations for named functions; arrow functions for callbacks.
- Rest parameters, never `arguments`. Default parameter values without side effects.
- `for...of` for arrays; `Object.entries`, `Object.keys` or `Object.values` for objects. Never `for...in` on an array.
- Every `switch` has a `default`. No fall-through from a non-empty case.
- Prefer immutable updates (spread, `map`, `filter`, `toSorted`) to in-place mutation of shared data.
- `async`/`await` over promise chains. Never leave a promise unhandled.

## TypeScript

- Keep `strict` on. Do not weaken compiler options to make an error go away.
- No `any`. Use `unknown` and narrow, or validate at the boundary with the project's schema library.
- Avoid type assertions (`as`) and non-null assertions (`!`). When one is needed, comment why it is safe.
- Annotate object literals with a type instead of asserting them.
- `interface` for object shapes; `type` for unions, tuples and mapped types.
- `T[]` for simple element types, `Array<T>` for complex ones; `readonly` where the array is not mutated.
- Optional properties (`name?: string`) for things that may be absent. Add `| null` or `| undefined` at the use site, not inside a type alias.
- Model variants with discriminated unions and make switches exhaustive:

```ts
type PaymentMethod =
  | { kind: 'card'; token: string }
  | { kind: 'bankTransfer'; iban: string };

function describe(method: PaymentMethod): string {
  switch (method.kind) {
    case 'card':
      return `card ending ${method.token.slice(-4)}`;
    case 'bankTransfer':
      return `transfer from ${method.iban.slice(0, 4)}`;
    default: {
      const unreachable: never = method;
      throw new Error(`Unhandled payment method: ${JSON.stringify(unreachable)}`);
    }
  }
}
```

- Mark class properties `readonly` when they are not reassigned. Use parameter properties for constructor-assigned fields. No `#private` fields where the project uses TypeScript `private`.
- Plain `enum` or a union of string literals, following the project. No `const enum`.

## Errors

- Throw `Error` or a subclass, always with `new`. Never throw strings or plain objects.
- Keep the cause when wrapping: `throw new InvoiceLoadError('invoice ' + id, { cause: err });`
- Type the catch variable as `unknown` and narrow before use.
- No empty `catch` without a comment explaining why.
- Keep `try` blocks around the code that can throw.
- Validate external input (requests, responses, environment variables, parsed JSON) at the boundary; trust types inside it.

## Documentation

- JSDoc (`/** ... */`) on exported functions, classes and types when the name and signature do not say enough. Do not restate types that TypeScript already declares.
- Line comments explain why.

## Plain JavaScript projects

The same rules apply except the type system. Use JSDoc type annotations if the project does, and whatever `// @ts-check` setup it already has. Do not convert files to TypeScript as part of an unrelated change.

## Suppressions

Scope to the line, name the rule, and give the reason:

```ts
// eslint-disable-next-line @typescript-eslint/no-explicit-any -- third-party callback is untyped upstream
```

Prefer `@ts-expect-error` with a reason over `@ts-ignore`, so the suppression fails when it is no longer needed.
