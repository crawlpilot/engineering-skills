# Unit testing: JavaScript and TypeScript

Use what the project already has. Vitest and Jest share most of their API; examples below use Vitest imports. For Jest, the same functions are globals or come from `@jest/globals`, and `vi` becomes `jest`. Do not add a second runner.

## Find and run

Read the `scripts` in `package.json` and the runner config (`vitest.config.*`, `jest.config.*`). Use the project's package manager, shown by its lockfile: `package-lock.json` (npm), `pnpm-lock.yaml` (pnpm), `yarn.lock` (Yarn).

| Goal | Vitest | Jest |
| --- | --- | --- |
| Everything, once | `npx vitest run` | `npx jest` |
| One file | `npx vitest run src/pricing.test.ts` | `npx jest src/pricing.test.ts` |
| By test name | `npx vitest run -t "negative quantity"` | `npx jest -t "negative quantity"` |

Plain `vitest` starts watch mode and does not exit; use `vitest run` in scripts and automation. Prefer the project's own script (`npm test`) when it exists. Test files sit next to the source as `*.test.ts` or under `__tests__/`, whichever the project does.

## Shape of a test

```ts
import { describe, expect, it } from 'vitest';

describe('PriceCalculator', () => {
  const calculator = new PriceCalculator(fixedTaxRates('0.20'));

  it('applies tax to the net price', () => {
    const total = calculator.totalFor(makeOrder({ items: [makeItem({ price: '10.00' })] }));

    expect(total).toEqual(money('12.00'));
  });

  it('rejects a negative quantity', () => {
    const order = makeOrder({ items: [makeItem({ quantity: -1 })] });

    expect(() => calculator.totalFor(order)).toThrow(/quantity/);
  });
});
```

- `toBe` for primitives and identity, `toEqual` for structural equality, `toStrictEqual` when `undefined` properties and types matter.
- Build inputs with factory functions that take a partial override: `makeItem(overrides: Partial<Item> = {})`.
- For a throwing call, pass a function to `expect`. Calling it directly throws before the assertion runs.
- `toBeCloseTo` for floats. Do not use floats for money.

## Same shape, many inputs

```ts
it.each([
  [0, 'FREE'],
  [1, 'STANDARD'],
  [49, 'STANDARD'],
  [50, 'BULK'],
])('picks tier for quantity %i', (quantity, expected) => {
  expect(tierFor(quantity)).toBe(expected);
});
```

## Async code

```ts
it('rejects when the gateway declines', async () => {
  const gateway = fakeGateway({ declines: true });

  await expect(charge(gateway, aCharge())).rejects.toThrow(PaymentDeclined);
});
```

- Always `await` or `return` the promise. An un-awaited assertion passes even when it would fail.
- `await expect(promise).resolves...` and `.rejects...` for promise outcomes.
- Enable the lint rule for floating promises if the project has typed linting.

## Time and randomness

Prefer passing `now` or a clock function into the code. When timers are the behaviour, use fake timers and restore them:

```ts
import { afterEach, beforeEach, expect, it, vi } from 'vitest';

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date('2026-01-15T10:00:00Z'));
});

afterEach(() => {
  vi.useRealTimers();
});

it('expires the session after 30 minutes', () => {
  const session = startSession();

  vi.advanceTimersByTime(30 * 60 * 1000);

  expect(session.isExpired()).toBe(true);
});
```

## Doubles

Prefer a hand-written fake that satisfies the interface:

```ts
class InMemoryOrderRepository implements OrderRepository {
  private readonly orders = new Map<string, Order>();

  async save(order: Order): Promise<void> {
    this.orders.set(order.id, order);
  }

  async findById(id: string): Promise<Order | undefined> {
    return this.orders.get(id);
  }
}
```

For an interaction that is the behaviour, pass a spy function as the dependency:

```ts
it('sends a welcome email on signup', async () => {
  const send = vi.fn<Mailer['send']>().mockResolvedValue(undefined);

  await new SignupService(new InMemoryUserRepository(), { send }).signUp('a@example.com');

  expect(send).toHaveBeenCalledExactlyOnceWith('a@example.com', expect.stringContaining('Welcome'));
});
```

- Prefer injecting dependencies over module mocking (`vi.mock`, `jest.mock`). Module mocks are hoisted, apply to the whole file, and break silently when an import path changes.
- If module mocking is unavoidable, mock the boundary module the code owns, not a third-party library's internals, and reset between tests with the runner's `restoreMocks` setting or `vi.restoreAllMocks()`.
- Type the double against the real interface so it fails to compile when the interface changes.
- If the matcher `toHaveBeenCalledExactlyOnceWith` is not available in the project's runner version, use `toHaveBeenCalledTimes(1)` with `toHaveBeenCalledWith(...)`.

## Component and DOM tests

If the change is UI code, use the project's existing testing library. Query by role and accessible name, assert on what the user sees, and avoid asserting on component internals or implementation state.

## Proving a test can fail

```bash
# edit the production line the test targets, then:
npx vitest run src/pricing.test.ts -t "applies tax"
git diff --stat   # must show no production change left behind
```

## Common mistakes

- A missing `await`, so the test finishes before the assertion.
- `it.only` or `describe.only` left in a commit; it silently disables the rest of the file.
- Snapshot tests for logic; snapshots get updated without being read.
- Mocks that leak between tests because they are never reset.
- Asserting on a mock's call arguments by index (`mock.calls[0][1]`) instead of with a matcher.
- Tests that pass alone but fail together because of shared module-level state.
