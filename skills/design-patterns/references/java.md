# Design patterns: Java

Modern Java makes several classic patterns a language feature. Reach for the lighter form first, and check the project's language level before using records, sealed types or pattern matching.

## Lighter forms first

| Classic pattern | Lighter form in modern Java |
| --- | --- |
| Strategy with a single method | A functional interface and a lambda or method reference |
| Command | `Runnable`, `Supplier<T>` or a small record implementing a functional interface |
| Factory for one type | A static factory method on the type |
| Visitor over a closed hierarchy | `sealed` interface with a pattern-matching `switch` |
| Value object with builder | A `record`; add a builder only when there are many optional fields |
| Singleton | One instance wired by the dependency-injection container, or an `enum` with a single constant |
| Template method | A method that takes the varying steps as functions |
| Observer with one listener | A direct call or a `Consumer<T>` |
| Decorator | A wrapper implementing the same interface; for functions, `Function.andThen` |

## Replacing a repeated conditional

Before: the same `switch` on a type code appears in several methods, and adding a variant means editing each one.

```java
sealed interface PaymentMethod permits Card, BankTransfer, Wallet {}
record Card(String token) implements PaymentMethod {}
record BankTransfer(String iban) implements PaymentMethod {}
record Wallet(String provider) implements PaymentMethod {}

Money feeFor(PaymentMethod method, Money amount) {
  return switch (method) {
    case Card c -> amount.percent(2.9).plus(Money.of("0.30"));
    case BankTransfer b -> Money.of("0.50");
    case Wallet w -> amount.percent(1.5);
  };
}
```

The compiler now rejects a `switch` that misses a variant, so a new payment method cannot be half-added. Choose this when the set of variants is closed and operations are added often. Choose an interface with a method per operation when variants are added often and operations are stable.

## Strategy as a function

```java
final class PriceCalculator {
  private final Function<Order, Money> discountPolicy;

  PriceCalculator(Function<Order, Money> discountPolicy) {
    this.discountPolicy = discountPolicy;
  }

  Money totalFor(Order order) {
    return order.subtotal().minus(discountPolicy.apply(order));
  }
}

new PriceCalculator(order -> Money.zero());
new PriceCalculator(SeasonalDiscounts::forOrder);
```

Introduce a named interface instead of `Function` when the strategy has more than one method, needs documentation of its contract, or appears in many signatures.

## Builder, only when it earns it

A record with a compact constructor covers validation and immutability:

```java
record RetryPolicy(int maxAttempts, Duration initialDelay, double multiplier) {
  RetryPolicy {
    if (maxAttempts < 1) throw new IllegalArgumentException("maxAttempts must be >= 1");
    Objects.requireNonNull(initialDelay, "initialDelay");
  }

  static RetryPolicy defaults() {
    return new RetryPolicy(3, Duration.ofMillis(200), 2.0);
  }

  RetryPolicy withMaxAttempts(int attempts) {
    return new RetryPolicy(attempts, initialDelay, multiplier);
  }
}
```

Add a builder when there are roughly five or more fields, several of them optional, and call sites become unreadable. If the project already uses a builder generator, follow it.

## Dependency injection without ceremony

Pass collaborators through the constructor and keep fields `final`. This is the pattern; a container only automates the wiring.

```java
final class InvoiceService {
  private final InvoiceRepository invoices;
  private final Clock clock;

  InvoiceService(InvoiceRepository invoices, Clock clock) {
    this.invoices = invoices;
    this.clock = clock;
  }
}
```

Introduce an interface for a collaborator when there is a second implementation or a test needs a fake. An interface with one implementation and no fake is indirection without benefit.

## Decorator for cross-cutting behaviour

```java
final class RetryingPaymentGateway implements PaymentGateway {
  private final PaymentGateway delegate;
  private final RetryPolicy policy;

  RetryingPaymentGateway(PaymentGateway delegate, RetryPolicy policy) {
    this.delegate = delegate;
    this.policy = policy;
  }

  @Override
  public Receipt charge(Charge charge) {
    return Retries.run(policy, () -> delegate.charge(charge));
  }
}
```

Check first whether the framework already provides this (interceptors, aspects, resilience libraries in use). Do not hand-roll what the project already has.

## Framework note

In a Spring codebase, the container already supplies singleton scope, factories, proxies and dependency injection. Use its mechanisms instead of writing parallel ones, and do not add a container to a project that wires by hand.

## Java-specific warning signs

- `AbstractBaseSomething` with one subclass.
- `SomethingImpl` as the only implementation of `Something`.
- A static utility class holding mutable state.
- Deep inheritance used to share helper methods.
- Reflection or annotations introduced to avoid passing an argument.
