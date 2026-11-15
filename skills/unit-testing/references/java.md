# Unit testing: Java

Use what the project already has. These are the defaults when a project has JUnit 5; do not add libraries that are not already on the test classpath.

## Find and run

| Build | Run everything | Run one class | Run one method |
| --- | --- | --- | --- |
| Maven | `mvn test` | `mvn test -Dtest=PriceCalculatorTest` | `mvn test -Dtest=PriceCalculatorTest#rejectsNegativeQuantity` |
| Gradle | `./gradlew test` | `./gradlew test --tests PriceCalculatorTest` | `./gradlew test --tests 'PriceCalculatorTest.rejectsNegativeQuantity'` |

Tests live in `src/test/java`, mirroring the package of the class under test. Class name is the subject plus `Test`.

## Shape of a test

```java
class PriceCalculatorTest {

  private final PriceCalculator calculator = new PriceCalculator(new FixedTaxRates(0.20));

  @Test
  void appliesTaxToNetPrice() {
    Money total = calculator.totalFor(order(item("book", "10.00")));

    assertThat(total).isEqualTo(Money.of("12.00"));
  }

  @Test
  void rejectsNegativeQuantity() {
    Order order = order(item("book", "10.00").withQuantity(-1));

    assertThatThrownBy(() -> calculator.totalFor(order))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("quantity");
  }
}
```

- Name methods for the behaviour. Follow the naming style already used in the test tree.
- Build inputs with small helper methods or test builders that take overrides (`order(...)`, `item(...)`), so each test shows only the values it depends on.
- With plain JUnit assertions, use `assertEquals(expected, actual)` in that order and `assertThrows(Type.class, () -> ...)`, then assert on the returned exception.

## Same shape, many inputs

```java
@ParameterizedTest
@CsvSource({
    "0,    FREE",
    "1,    STANDARD",
    "49,   STANDARD",
    "50,   BULK"
})
void picksTierByQuantity(int quantity, Tier expected) {
  assertThat(Tier.forQuantity(quantity)).isEqualTo(expected);
}
```

Use `@MethodSource` when arguments are objects. Keep the expected value in the table, never computed.

## Time, randomness, files

- Inject `java.time.Clock` and pass `Clock.fixed(Instant.parse("2026-01-15T10:00:00Z"), ZoneOffset.UTC)` in tests. Code that calls `Instant.now()` with no clock is the seam to fix.
- Inject the random source, or a supplier of values.
- Use `@TempDir Path dir` for files. Never write to a fixed path.

## Doubles

Prefer a hand-written fake for anything with state:

```java
final class InMemoryOrderRepository implements OrderRepository {
  private final Map<OrderId, Order> orders = new HashMap<>();
  @Override public void save(Order order) { orders.put(order.id(), order); }
  @Override public Optional<Order> findById(OrderId id) { return Optional.ofNullable(orders.get(id)); }
}
```

With Mockito, when the project uses it:

```java
@ExtendWith(MockitoExtension.class)
class SignupServiceTest {
  @Mock Mailer mailer;

  @Test
  void sendsWelcomeEmailOnSignup() {
    new SignupService(new InMemoryUserRepository(), mailer).signUp("a@example.com");

    verify(mailer).send(eq("a@example.com"), contains("Welcome"));
  }
}
```

- Stub with `when(...).thenReturn(...)` only what the test needs. Leave strict stubbing on; an unused stub is a sign the test is wrong.
- Verify only interactions that are the behaviour. Do not verify every call, and avoid `verifyNoMoreInteractions` as a habit.
- Do not mock value types, records, collections or the class under test. Avoid static and constructor mocking; it marks a missing seam.

## Proving a test can fail

Change the production line the test targets, run just that test, confirm the failure message names the right expectation, then revert:

```bash
mvn test -Dtest=PriceCalculatorTest#appliesTaxToNetPrice
git diff --stat   # must show no production change left behind
```

## Common mistakes

- Asserting on `toString()` output instead of fields or equality.
- `@BeforeEach` that hides the values a test depends on.
- Shared static mutable fixtures, which make tests order-dependent.
- `Thread.sleep` in a unit test. Inject a clock or use a synchronous executor.
- Catching an exception in the test and asserting inside the catch; the test passes when nothing is thrown.
