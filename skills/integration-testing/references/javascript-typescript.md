# Integration testing: JavaScript and TypeScript

Use what the project already has. Examples use Vitest; the structure is the same in Jest. Check library APIs against the versions installed.

## Separate them from unit tests

Follow the project's convention: a filename suffix (`*.int.test.ts`, `*.integration.test.ts`), a directory, or a separate runner config or project.

```bash
npx vitest run --config vitest.integration.config.ts
npx vitest run src/orders/order-repository.int.test.ts
```

Integration tests usually need a longer timeout and should not run in the default fast suite. Set the timeout in the integration config, not per test.

## Real database with Testcontainers

```ts
import { PostgreSqlContainer, type StartedPostgreSqlContainer } from '@testcontainers/postgresql';
import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest';

describe('OrderRepository', () => {
  let container: StartedPostgreSqlContainer;
  let db: Database;
  let repository: OrderRepository;

  beforeAll(async () => {
    container = await new PostgreSqlContainer('postgres:16-alpine').start();
    db = await connect(container.getConnectionUri());
    await runMigrations(db); // the project's real migrations
  }, 60_000);

  afterAll(async () => {
    await db.close();
    await container.stop();
  });

  beforeEach(async () => {
    await truncateAll(db); // each test starts from empty tables
    repository = new OrderRepository(db);
  });

  it('finds a saved order by id', async () => {
    const order = makeOrder({ id: randomUUID() });

    await repository.save(order);

    expect(await repository.findById(order.id)).toEqual(order);
  });

  it('rejects a duplicate order id', async () => {
    const order = makeOrder({ id: randomUUID() });
    await repository.save(order);

    await expect(repository.save(order)).rejects.toThrow(DuplicateOrderError);
  });
});
```

- To share one container across files, start it in the runner's global setup and pass the connection string to tests the way the project already does.
- Pin the image to the major version production runs, and run the real migrations (Prisma, Drizzle, Knex, TypeORM or plain SQL).
- Use the production database engine. An in-memory or SQLite substitute hides type, constraint and locking differences.
- Test files run in parallel by default. Isolate by unique keys or a schema per worker, or run the integration project serially.
- Close pools and stop containers in `afterAll`; a leaked handle keeps the process alive and hangs CI.

## Testing your own HTTP API

Drive the app through real routing, validation and serialisation without opening a public port: `supertest` for Express-style apps, `app.inject()` for Fastify, `app.request()` for Hono, or the framework's own testing module.

```ts
it('returns 404 for an unknown order', async () => {
  const response = await request(buildApp({ db })).get(`/orders/${randomUUID()}`);

  expect(response.status).toBe(404);
});
```

## HTTP dependencies

Stub at the network level so the real client code, serialisation and error handling run. Mock Service Worker (MSW) intercepts `fetch` and Node HTTP requests:

```ts
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer();

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it('surfaces a declined payment', async () => {
  server.use(
    http.post('https://pay.example.test/v1/charges', () =>
      HttpResponse.json({ code: 'card_declined' }, { status: 402 }),
    ),
  );
  const client = new PaymentClient({ baseUrl: 'https://pay.example.test', timeoutMs: 2000 });

  await expect(client.charge(makeCharge())).rejects.toThrow(PaymentDeclined);
});
```

- `onUnhandledRequest: 'error'` makes an unexpected outbound call fail the test instead of reaching the network.
- Cover the failure modes: an error status, a response slower than the client timeout, a network error (`HttpResponse.error()`), and a malformed body.
- Keep handlers honest with a contract test against the provider's published schema. If the provider publishes an OpenAPI document, generate or validate the stubs from it.

## Asynchronous behaviour

Wait on a condition with a timeout, never a fixed sleep:

```ts
import { expect, it, vi } from 'vitest';

it('publishes an order-placed event', async () => {
  const orderId = randomUUID();

  await placeOrder(db, broker, orderId);

  await vi.waitFor(() => expect(broker.received()).toContainEqual(orderPlaced(orderId)), {
    timeout: 10_000,
  });
});
```

In Jest, use the testing library's `waitFor` if present, or a small polling helper with a deadline. Do not use fake timers in integration tests; real I/O does not advance with them.

## Browser end-to-end tests

Playwright tests are a separate, slower category. Keep them to a few critical user journeys, select by role and accessible name, rely on the tool's auto-waiting rather than fixed timeouts, and give each test its own data.

## Stability checks

```bash
for i in 1 2 3; do npx vitest run --config vitest.integration.config.ts src/orders/order-repository.int.test.ts || break; done
```

Typical causes of flakiness: a missing `await`, shared rows across parallel files, fixed ports, handlers or mocks not reset between tests, and unclosed connections.
