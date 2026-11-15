# Unit testing: Kotlin

Use what the project already has. Kotlin projects commonly use JUnit 5 with kotlin.test or AssertJ assertions, or Kotest; follow whichever is on the test classpath and do not add another.

## Find and run

| Goal | Gradle |
| --- | --- |
| Everything | `./gradlew test` |
| One class | `./gradlew test --tests PriceCalculatorTest` |
| One method | `./gradlew test --tests 'PriceCalculatorTest.rejectsNegativeQuantity'` |
| One module | `./gradlew :billing:test` |

On Android, local unit tests run with `./gradlew testDebugUnitTest`. Tests live in `src/test/kotlin`, mirroring the package of the code under test.

## Shape of a test

```kotlin
class PriceCalculatorTest {

    private val calculator = PriceCalculator(FixedTaxRates("0.20".toBigDecimal()))

    @Test
    fun appliesTaxToNetPrice() {
        val total = calculator.totalFor(order(item(price = "10.00")))

        assertEquals(Money("12.00"), total)
    }

    @Test
    fun rejectsNegativeQuantity() {
        val order = order(item(quantity = -1))

        val error = assertFailsWith<IllegalArgumentException> { calculator.totalFor(order) }

        assertContains(error.message.orEmpty(), "quantity")
    }
}
```

- Build inputs with factory functions that use default arguments, so each test names only the values it depends on: `fun item(price: String = "1.00", quantity: Int = 1)`.
- `assertEquals(expected, actual)` in that order. `assertFailsWith<T> { }` returns the exception for further checks.
- Follow the naming style already in the test tree. Backtick names with spaces are common on the JVM but are not allowed by the Android Kotlin style guide and do not work on every target; do not introduce them into a codebase that avoids them.

## Same shape, many inputs

```kotlin
@ParameterizedTest
@CsvSource(
    "0,  FREE",
    "1,  STANDARD",
    "49, STANDARD",
    "50, BULK",
)
fun picksTierByQuantity(quantity: Int, expected: Tier) {
    assertEquals(expected, Tier.forQuantity(quantity))
}
```

In Kotest, use the project's existing spec style with `withData` for table-driven cases.

## Coroutines and flows

```kotlin
@Test
fun retriesOnceThenSucceeds() = runTest {
    val gateway = FakeGateway(failuresBeforeSuccess = 1)

    val receipt = RetryingClient(gateway).charge(aCharge())

    assertEquals(2, gateway.attempts)
    assertEquals(Receipt.Paid, receipt)
}
```

- Use `runTest` from `kotlinx-coroutines-test`. It skips `delay` calls with virtual time, so tests never wait in real time.
- Inject dispatchers into the code under test and pass a test dispatcher. Code that hard-codes `Dispatchers.IO` is the seam to fix.
- Do not use `runBlocking` with real delays, or `Thread.sleep`.
- For `Flow`, collect to a list for finite flows; for hot flows use the project's existing helper (commonly Turbine) rather than hand-rolled collection with delays.

## Time, randomness, files

- Inject `java.time.Clock` (or `kotlinx.datetime.Clock` if the project uses it) and pass a fixed one.
- Inject the random source.
- `@TempDir` for files.

## Doubles

Prefer a hand-written fake. Kotlin makes these short:

```kotlin
class InMemoryOrderRepository : OrderRepository {
    private val orders = mutableMapOf<OrderId, Order>()
    override fun save(order: Order) { orders[order.id] = order }
    override fun findById(id: OrderId): Order? = orders[id]
}
```

For a single-method interface declared with `fun interface`, pass a lambda instead of a mock.

With MockK, when the project uses it and an interaction is the behaviour:

```kotlin
@Test
fun sendsWelcomeEmailOnSignup() {
    val mailer = mockk<Mailer>(relaxUnitFun = true)

    SignupService(InMemoryUserRepository(), mailer).signUp("a@example.com")

    verify(exactly = 1) { mailer.send("a@example.com", match { "Welcome" in it }) }
}
```

- Use `coEvery` and `coVerify` for suspending functions.
- Avoid fully relaxed mocks (`relaxed = true`); they return defaults for everything and hide missing stubs.
- Do not mock data classes, sealed types or the class under test. `mockkStatic` and `mockkObject` mark a missing seam.
- Classes are final by default. If Mockito is the project's library, check that its inline mock maker or the `all-open` plugin is already configured before assuming a class can be mocked.

## Proving a test can fail

```bash
# edit the production line the test targets, then:
./gradlew test --tests 'PriceCalculatorTest.appliesTaxToNetPrice'
git diff --stat   # must show no production change left behind
```

## Common mistakes

- Asserting on a data class's `toString()` instead of equality.
- `lateinit var` fixtures set in `@BeforeEach` that hide the values a test depends on.
- `!!` in tests where an explicit assertion would give a clearer failure.
- Comparing `BigDecimal` values with different scales using `equals`; use `compareTo` or a money type.
- Shared mutable state in a `companion object`.
