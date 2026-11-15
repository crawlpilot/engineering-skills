# Design patterns: Python

Functions are values, modules are namespaces and duck typing removes the need for many interfaces. Most classic patterns shrink to a few lines, and a class is often not needed at all.

## Lighter forms first

| Classic pattern | Lighter form in Python |
| --- | --- |
| Strategy | Pass a function |
| Command | A function plus `functools.partial`, or a small dataclass with `__call__` |
| Factory | A plain function, or a `classmethod` constructor |
| Singleton | A module-level object, created once at the composition root |
| Decorator | A function decorator, or a wrapper class with the same methods |
| Template method | A function taking the varying steps as callables |
| Iterator | A generator function |
| Observer with one listener | A callback |
| Adapter | A small function or wrapper class |
| Builder | Keyword arguments with defaults, or a `dataclass` |
| Scoped resource | A context manager (`with`) |
| Visitor over a closed set | `match` on dataclasses, or `functools.singledispatch` |

## Replacing a repeated conditional

Before: the same `if kind == ...` chain appears in several functions.

```python
def card_fee(amount: Decimal) -> Decimal:
    return amount * Decimal("0.029") + Decimal("0.30")


def bank_transfer_fee(amount: Decimal) -> Decimal:
    return Decimal("0.50")


def wallet_fee(amount: Decimal) -> Decimal:
    return amount * Decimal("0.015")


FEE_BY_METHOD: dict[PaymentMethod, Callable[[Decimal], Decimal]] = {
    PaymentMethod.CARD: card_fee,
    PaymentMethod.BANK_TRANSFER: bank_transfer_fee,
    PaymentMethod.WALLET: wallet_fee,
}


def fee_for(method: PaymentMethod, amount: Decimal) -> Decimal:
    return FEE_BY_METHOD[method](amount)
```

One table replaces every chain. A test can assert that every `PaymentMethod` member has an entry, so a new method cannot be half-added. When variants carry different data, use dataclasses and `match`:

```python
@dataclass(frozen=True)
class Card:
    token: str


@dataclass(frozen=True)
class BankTransfer:
    iban: str


def describe(method: Card | BankTransfer) -> str:
    match method:
        case Card(token=token):
            return f"card ending {token[-4:]}"
        case BankTransfer(iban=iban):
            return f"transfer from {iban[:4]}"
```

## Strategy as a function

```python
class PriceCalculator:
    def __init__(self, discount_policy: Callable[[Order], Decimal]):
        self._discount_policy = discount_policy

    def total_for(self, order: Order) -> Decimal:
        return order.subtotal - self._discount_policy(order)


PriceCalculator(lambda order: Decimal("0"))
PriceCalculator(seasonal_discount)
```

Define a `Protocol` when the strategy has more than one method or its contract needs a name:

```python
class DiscountPolicy(Protocol):
    def discount_for(self, order: Order) -> Decimal: ...
    def describe(self) -> str: ...
```

A `Protocol` is structural, so implementations need not inherit from it. Use an abstract base class only when shared implementation is needed.

## Configuration objects instead of builders

```python
@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    initial_delay: float = 0.2
    multiplier: float = 2.0

    def __post_init__(self):
        if self.max_attempts < 1:
            raise ValueError(f"max_attempts must be >= 1, got {self.max_attempts}")


policy = RetryPolicy(max_attempts=5)
stricter = dataclasses.replace(policy, max_attempts=2)
```

Keyword arguments with defaults give what a builder gives elsewhere. If the project uses a model library such as Pydantic or attrs, follow it.

## Dependency injection without a framework

Pass collaborators in and build the object graph in one place, usually near `main()` or the application factory.

```python
class InvoiceService:
    def __init__(self, invoices: InvoiceRepository, now: Callable[[], datetime]):
        self._invoices = invoices
        self._now = now


service = InvoiceService(SqlInvoiceRepository(engine), now=lambda: datetime.now(UTC))
```

Avoid importing a global client inside the function that uses it; that is the hidden dependency that makes code untestable. If the framework has its own injection (FastAPI `Depends`, pytest fixtures), use it.

## Decorators and context managers for cross-cutting behaviour

```python
def retrying(policy: RetryPolicy):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return run_with_retries(policy, lambda: fn(*args, **kwargs))
        return wrapper
    return decorate


@contextmanager
def timed(metric: str):
    start = time.monotonic()
    try:
        yield
    finally:
        record(metric, time.monotonic() - start)
```

Always use `functools.wraps`. Check first whether a library already in the project provides the behaviour.

## Python-specific warning signs

- A class with only `__init__` and one method: it is a function.
- A class used only as a namespace for static methods: it is a module.
- Abstract base classes with one concrete subclass.
- Getters and setters around plain attributes.
- Metaclasses, `__getattr__` tricks or monkey-patching to avoid passing an argument.
- A hand-written singleton class with `__new__` overridden.
- Deep inheritance or mixin stacks used to share helpers.
