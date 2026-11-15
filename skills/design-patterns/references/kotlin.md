# Design patterns: Kotlin

Kotlin builds several classic patterns into the language. Use the language feature before writing the pattern by hand.

## Lighter forms first

| Classic pattern | Lighter form in Kotlin |
| --- | --- |
| Strategy | A function type parameter: `(Order) -> Money` |
| Command | A lambda, or a `fun interface` |
| Singleton | `object` |
| Builder | Default and named arguments; `copy()` on a data class |
| Factory | A top-level function, or `operator fun invoke` on a companion object |
| Decorator | Class delegation with `by` |
| Visitor over a closed hierarchy | `sealed interface` with an exhaustive `when` |
| State | `sealed interface` of states, with a pure transition function |
| Observer | `Flow` or `StateFlow` |
| Lazy initialisation | `by lazy` |
| Adapter | An extension function |
| Template method | A higher-order function taking the varying steps |
| Scoped resource | `use { }` |
| Type-safe configuration | A lambda with receiver, only when a real configuration language is needed |

## Replacing a repeated conditional

Before: the same `when (type)` on a string or enum code appears in several functions.

```kotlin
sealed interface PaymentMethod {
    data class Card(val token: String) : PaymentMethod
    data class BankTransfer(val iban: String) : PaymentMethod
    data class Wallet(val provider: String) : PaymentMethod
}

fun feeFor(method: PaymentMethod, amount: Money): Money = when (method) {
    is PaymentMethod.Card -> amount.percent(2.9) + Money("0.30")
    is PaymentMethod.BankTransfer -> Money("0.50")
    is PaymentMethod.Wallet -> amount.percent(1.5)
}
```

Because `when` is used as an expression with no `else`, the compiler rejects it when a variant is missing. Adding an `else` branch throws that guarantee away. Choose this when the set of variants is closed and operations are added often. Choose an interface with a method per operation when variants are added often and operations are stable.

## Strategy as a function

```kotlin
class PriceCalculator(private val discountPolicy: (Order) -> Money) {
    fun totalFor(order: Order): Money = order.subtotal - discountPolicy(order)
}

PriceCalculator { Money.ZERO }
PriceCalculator(::seasonalDiscount)
```

Use a `fun interface` instead of a bare function type when the strategy deserves a name and documentation, or appears in many signatures:

```kotlin
fun interface DiscountPolicy {
    fun discountFor(order: Order): Money
}

val none = DiscountPolicy { Money.ZERO }
```

## Configuration without a builder

```kotlin
data class RetryPolicy(
    val maxAttempts: Int = 3,
    val initialDelay: Duration = 200.milliseconds,
    val multiplier: Double = 2.0,
) {
    init {
        require(maxAttempts >= 1) { "maxAttempts must be >= 1, was $maxAttempts" }
    }
}

val policy = RetryPolicy(maxAttempts = 5)
val stricter = policy.copy(maxAttempts = 2)
```

Default and named arguments remove nearly every reason for a builder. Write one only when Java callers need it. Note that `copy()` runs `init` validation but bypasses any factory function, so keep invariants in `init`.

## Decorator by delegation

```kotlin
class RetryingPaymentGateway(
    private val delegate: PaymentGateway,
    private val policy: RetryPolicy,
) : PaymentGateway by delegate {

    override suspend fun charge(charge: Charge): Receipt =
        retrying(policy) { delegate.charge(charge) }
}
```

`by delegate` forwards every other interface method, so the wrapper overrides only what it changes.

## State as data

```kotlin
sealed interface OrderState {
    data object Draft : OrderState
    data class Submitted(val at: Instant) : OrderState
    data class Shipped(val trackingId: String) : OrderState
    data object Cancelled : OrderState
}

fun OrderState.on(event: OrderEvent, now: Instant): OrderState = when (this) {
    OrderState.Draft -> when (event) {
        OrderEvent.Submit -> OrderState.Submitted(now)
        OrderEvent.Cancel -> OrderState.Cancelled
        else -> this
    }
    is OrderState.Submitted -> when (event) {
        is OrderEvent.Ship -> OrderState.Shipped(event.trackingId)
        OrderEvent.Cancel -> OrderState.Cancelled
        else -> this
    }
    is OrderState.Shipped, OrderState.Cancelled -> this
}
```

A pure transition function is trivial to test and keeps every legal transition in one place. Whether an unexpected event is ignored, as here, or rejected is a decision to make explicitly.

## Dependency injection

Constructor parameters are the pattern. A container (Hilt, Koin, Spring) only automates the wiring; use the one the project has and do not add one to a project that wires by hand.

```kotlin
class InvoiceService(
    private val invoices: InvoiceRepository,
    private val clock: Clock,
    private val ioDispatcher: CoroutineDispatcher,
)
```

Introduce an interface for a collaborator when there is a second implementation or a test needs a fake.

## Kotlin-specific warning signs

- A custom DSL with lambdas-with-receiver where named arguments would do.
- Extension functions used to bolt behaviour onto types the project owns, instead of putting it in the type.
- Operator overloading or infix functions for operations that are not obviously arithmetic or collection-like.
- `object` singletons holding mutable state or doing I/O, which hide dependencies.
- Deeply nested scope functions.
- An interface with one implementation and an `Impl` suffix.
- Inheritance from an `open` class to share helpers; prefer composition or delegation.
- Reified generics and inline functions used for cleverness where a plain parameter would do.
