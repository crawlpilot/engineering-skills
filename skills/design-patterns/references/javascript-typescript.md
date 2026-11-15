# Design patterns: JavaScript and TypeScript

Functions are values, objects are cheap, and modules are singletons. Most classic patterns become a function or a plain object, and a class is often unnecessary.

## Lighter forms first

| Classic pattern | Lighter form in JavaScript and TypeScript |
| --- | --- |
| Strategy | Pass a function |
| Command | A closure, or an object with the function and its arguments |
| Factory | A function returning an object |
| Singleton | A module-level value, created once at the composition root |
| Builder | An options object with defaults |
| Decorator | A higher-order function wrapping another function |
| Observer | A callback, `EventTarget`, or the framework's own reactivity |
| Iterator | A generator function |
| Adapter | A small wrapper function or object |
| Visitor over a closed set | A discriminated union with an exhaustive `switch` |
| State | A discriminated union with a pure reducer |
| Template method | A function taking the varying steps as callbacks |
| Scoped resource | `try`/`finally`, or `using` where the project's targets support it |

## Replacing a repeated conditional

Before: the same `if (kind === ...)` chain appears in several functions.

```ts
type PaymentMethod =
  | { kind: 'card'; token: string }
  | { kind: 'bankTransfer'; iban: string }
  | { kind: 'wallet'; provider: string };

const FEE_BY_KIND: Record<PaymentMethod['kind'], (amount: number) => number> = {
  card: (amount) => Math.round(amount * 0.029) + 30,
  bankTransfer: () => 50,
  wallet: (amount) => Math.round(amount * 0.015),
};

function feeFor(method: PaymentMethod, amountInCents: number): number {
  return FEE_BY_KIND[method.kind](amountInCents);
}
```

`Record<PaymentMethod['kind'], ...>` makes a missing entry a compile error, so a new payment method cannot be half-added. When each variant needs its own data, use a `switch` on the discriminant with a `never` check in `default`; the coding-standards reference shows that form.

## Strategy as a function

```ts
type DiscountPolicy = (order: Order) => number;

class PriceCalculator {
  constructor(private readonly discountPolicy: DiscountPolicy) {}

  totalFor(order: Order): number {
    return order.subtotal - this.discountPolicy(order);
  }
}

new PriceCalculator(() => 0);
new PriceCalculator(seasonalDiscount);
```

Define an interface with several methods only when the strategy really has several operations. Often the calculator need not be a class either:

```ts
function totalFor(order: Order, discountPolicy: DiscountPolicy): number {
  return order.subtotal - discountPolicy(order);
}
```

## Options objects instead of builders

```ts
interface RetryPolicy {
  readonly maxAttempts: number;
  readonly initialDelayMs: number;
  readonly multiplier: number;
}

const DEFAULT_RETRY_POLICY: RetryPolicy = { maxAttempts: 3, initialDelayMs: 200, multiplier: 2 };

function retryPolicy(overrides: Partial<RetryPolicy> = {}): RetryPolicy {
  const policy = { ...DEFAULT_RETRY_POLICY, ...overrides };
  if (policy.maxAttempts < 1) {
    throw new RangeError(`maxAttempts must be >= 1, got ${policy.maxAttempts}`);
  }
  return policy;
}

const policy = retryPolicy({ maxAttempts: 5 });
```

## Dependency injection without a framework

Pass collaborators in and build the object graph in one place, near the entry point.

```ts
interface InvoiceServiceDeps {
  readonly invoices: InvoiceRepository;
  readonly now: () => Date;
}

function createInvoiceService({ invoices, now }: InvoiceServiceDeps) {
  return {
    async overdue(customerId: string): Promise<Invoice[]> {
      const all = await invoices.forCustomer(customerId);
      return all.filter((invoice) => !invoice.paid && invoice.dueDate < now());
    },
  };
}

const service = createInvoiceService({ invoices: sqlInvoices(db), now: () => new Date() });
```

Importing a shared client directly inside the module that uses it is the hidden dependency that forces module mocking in tests. If the framework has its own injection (NestJS, Angular), use it; do not add a container to a project that wires by hand.

## Wrapping behaviour with higher-order functions

```ts
function withRetry<Args extends unknown[], Result>(
  fn: (...args: Args) => Promise<Result>,
  policy: RetryPolicy,
): (...args: Args) => Promise<Result> {
  return async (...args) => {
    let delay = policy.initialDelayMs;
    for (let attempt = 1; ; attempt++) {
      try {
        return await fn(...args);
      } catch (error) {
        if (attempt >= policy.maxAttempts) throw error;
        await sleep(delay);
        delay *= policy.multiplier;
      }
    }
  };
}

const chargeWithRetry = withRetry(gateway.charge.bind(gateway), policy);
```

Check first whether a library already in the project provides the behaviour. Note the `bind`: passing a method without it loses `this`.

## State as a reducer

```ts
type OrderState =
  | { status: 'draft' }
  | { status: 'submitted'; at: Date }
  | { status: 'shipped'; trackingId: string }
  | { status: 'cancelled' };

type OrderEvent = { type: 'submit'; at: Date } | { type: 'ship'; trackingId: string } | { type: 'cancel' };

function transition(state: OrderState, event: OrderEvent): OrderState {
  switch (state.status) {
    case 'draft':
      if (event.type === 'submit') return { status: 'submitted', at: event.at };
      if (event.type === 'cancel') return { status: 'cancelled' };
      return state;
    case 'submitted':
      if (event.type === 'ship') return { status: 'shipped', trackingId: event.trackingId };
      if (event.type === 'cancel') return { status: 'cancelled' };
      return state;
    case 'shipped':
    case 'cancelled':
      return state;
    default: {
      const unreachable: never = state;
      throw new Error(`Unhandled state: ${JSON.stringify(unreachable)}`);
    }
  }
}
```

A pure transition function keeps every legal transition in one place. Whether an unexpected event is ignored, as here, or rejected is a decision to make explicitly. Reach for a state-machine library only when the project already has one or the machine is large.

## Warning signs

- A class with only a constructor and one method: it is a function.
- A class of static methods: it is a module.
- A hand-written singleton with `getInstance()`: the module system already gives you one instance.
- Deep inheritance, or mixins, used to share helpers.
- An interface with one implementation and no test fake.
- A homemade event bus connecting parts that could call each other directly.
- Custom decorators or `Proxy` objects introduced to avoid passing an argument.
- Type-level programming (deep conditional and mapped types) that no caller benefits from.
- Abstractions over a framework that hide it without replacing anything it does.
