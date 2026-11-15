# Integration testing: Java

Use what the project already has. These are common defaults; check versions and APIs against the project's dependencies.

## Separate them from unit tests

| Build | Convention | Run |
| --- | --- | --- |
| Maven | Classes named `*IT`, run by the Failsafe plugin in the `integration-test` phase | `mvn verify` |
| Gradle | A separate source set and task (for example `integrationTest`), or a JUnit tag | `./gradlew integrationTest` |
| Either | `@Tag("integration")` with include and exclude filters | as configured |

Follow whichever the project uses. Do not put container-backed tests in the default unit test task.

## Real database with Testcontainers

```java
@Testcontainers
class OrderRepositoryIT {

  @Container
  static final PostgreSQLContainer<?> postgres =
      new PostgreSQLContainer<>("postgres:16-alpine");

  private OrderRepository repository;

  @BeforeEach
  void setUp() {
    DataSource dataSource = dataSourceFor(postgres);
    migrate(dataSource);               // the project's real migrations
    truncateAll(dataSource);           // each test starts from empty tables
    repository = new JdbcOrderRepository(dataSource);
  }

  @Test
  void findsSavedOrderById() {
    Order order = anOrder().withId(OrderId.random()).build();

    repository.save(order);

    assertThat(repository.findById(order.id())).contains(order);
  }

  @Test
  void rejectsDuplicateOrderId() {
    Order order = anOrder().withId(OrderId.random()).build();
    repository.save(order);

    assertThatThrownBy(() -> repository.save(order))
        .isInstanceOf(DuplicateOrderException.class);
  }
}
```

- A `static` container is started once per class. To share one across the suite, use the project's existing base class or singleton-container setup rather than inventing a new one.
- Pin the image to the major version production runs. Do not use `latest`.
- Run the real migrations (Flyway, Liquibase) so the schema under test is the schema that ships.
- Use the same database engine as production. An embedded substitute such as H2 hides dialect, type and locking differences.
- Reset state per test by truncating or by unique keys. Do not rely on test order.
- With Spring Boot, wire container properties through `@DynamicPropertySource` or `@ServiceConnection`, and prefer a slice (`@DataJpaTest`, `@WebMvcTest`) over the full context when the seam allows it.

## HTTP dependencies

Stub at the network level so the real client, serialisation and error handling run:

```java
@RegisterExtension
static WireMockExtension paymentApi =
    WireMockExtension.newInstance().options(wireMockConfig().dynamicPort()).build();

@Test
void surfacesDeclinedPayment() {
  paymentApi.stubFor(post("/v1/charges")
      .willReturn(aResponse().withStatus(402).withBody("{\"code\":\"card_declined\"}")));

  PaymentClient client = new PaymentClient(paymentApi.baseUrl(), Duration.ofSeconds(2));

  assertThatThrownBy(() -> client.charge(aCharge()))
      .isInstanceOf(PaymentDeclinedException.class);
}
```

Cover the failure modes explicitly: a 5xx, a slow response past the client timeout (`withFixedDelay`), a dropped connection (`withFault`), and a malformed body. Keep stubs honest with a contract test against the provider's published schema or a consumer-driven contract tool the project already uses.

## Asynchronous behaviour

Wait on a condition, never a fixed sleep:

```java
await().atMost(Duration.ofSeconds(10))
    .untilAsserted(() -> assertThat(outbox.published()).contains(orderPlaced(orderId)));
```

Awaitility is the usual library. If it is not on the classpath, write a small polling helper with a deadline.

## Messaging

Use a container for the real broker (Kafka, RabbitMQ) when the seam is your producer or consumer configuration. Give each test its own topic or queue name and consumer group so runs are independent.

## Stability checks

```bash
mvn verify -Dit.test=OrderRepositoryIT        # one class
for i in 1 2 3; do mvn -q verify -Dit.test=OrderRepositoryIT || break; done
```

Typical causes of flakiness: fixed sleeps, shared tables without cleanup, fixed ports, reliance on wall-clock time, and test order.
