# Integration testing: Kotlin

Use what the project already has. The JVM tooling is the same as for Java; this file covers what differs in Kotlin. Check library APIs against the versions the project uses.

## Separate them from unit tests

Follow the project's convention: a separate Gradle source set and task (commonly `integrationTest`), or a JUnit tag with include and exclude filters.

```bash
./gradlew integrationTest
./gradlew integrationTest --tests OrderRepositoryIT
```

On Android, instrumented tests in `src/androidTest` run on a device or emulator with `./gradlew connectedDebugAndroidTest`. They are a different category from the server-side tests below; follow the project's existing setup for them.

## Real database with Testcontainers

```kotlin
@Testcontainers
class OrderRepositoryIT {

    companion object {
        @Container
        @JvmStatic
        val postgres = PostgreSQLContainer("postgres:16-alpine")
    }

    private lateinit var repository: OrderRepository

    @BeforeEach
    fun setUp() {
        val dataSource = dataSourceFor(postgres)
        migrate(dataSource)       // the project's real migrations
        truncateAll(dataSource)   // each test starts from empty tables
        repository = JdbcOrderRepository(dataSource)
    }

    @Test
    fun findsSavedOrderById() {
        val order = anOrder(id = OrderId.random())

        repository.save(order)

        assertEquals(order, repository.findById(order.id))
    }

    @Test
    fun rejectsDuplicateOrderId() {
        val order = anOrder(id = OrderId.random())
        repository.save(order)

        assertFailsWith<DuplicateOrderException> { repository.save(order) }
    }
}
```

- A shared container must be a static field: declare it in the `companion object` with `@JvmStatic`. Without `@JvmStatic` the JUnit extension treats it as per-instance or does not find it.
- Older Testcontainers versions declare containers with a self-referencing generic and need `PostgreSQLContainer<Nothing>("...")` in Kotlin. Match what the project's version requires.
- Pin the image to the major version production runs, run the real migrations, and use the production database engine rather than an embedded substitute.
- With Spring Boot, wire container properties through `@DynamicPropertySource` (in the companion object, `@JvmStatic`) or `@ServiceConnection`.

## Ktor services

Drive the application through its test host so routing, serialisation and plugins run for real:

```kotlin
@Test
fun returns404ForUnknownOrder() = testApplication {
    application { module(testDependencies(db)) }

    val response = client.get("/orders/${UUID.randomUUID()}")

    assertEquals(HttpStatusCode.NotFound, response.status)
}
```

To test an outbound Ktor `HttpClient`, the client library's `MockEngine` lets the real client code, serialisation and error handling run against canned responses.

## HTTP dependencies

For non-Ktor clients, stub at the network level with WireMock or OkHttp's `MockWebServer`, as in the Java reference. Cover an error status, a response slower than the client timeout, a dropped connection and a malformed body. Keep stubs honest with a contract test.

## Coroutines and asynchronous behaviour

- Use `runTest` for suspending test bodies. Its virtual time applies only to the test's own dispatcher; real I/O against a container still takes real time, so set an explicit `timeout` on `runTest` for slow operations.
- To wait for an asynchronous effect in another component, poll for the condition with a deadline (Awaitility, or `withTimeout` around a polling loop that uses real time). Never a fixed `delay`.
- For a `Flow` fed by a real source, collect with a timeout and assert on the collected values.

```kotlin
await().atMost(Duration.ofSeconds(10)).untilAsserted {
    assertContains(outbox.published(), orderPlaced(orderId))
}
```

## Persistence libraries

- Exposed, jOOQ, JDBI and Spring Data all generate SQL whose behaviour depends on the real engine. Test the queries against the real database, not against a mocked DSL.
- For Room on Android, use the in-memory database builder in instrumented tests and the migration test helper for schema changes.

## Stability checks

```bash
for i in 1 2 3; do ./gradlew -q integrationTest --tests OrderRepositoryIT --rerun-tasks || break; done
```

`--rerun-tasks` matters: without it Gradle reports the cached result and does not run the tests again. Typical causes of flakiness are the same as in Java, plus real delays hidden inside coroutine code that the test assumed were virtual.
