from orders.store import Order, OrderStore


def make_store(count: int, cancelled_every: int = 0) -> OrderStore:
    store = OrderStore()
    for i in range(1, count + 1):
        status = "cancelled" if cancelled_every and i % cancelled_every == 0 else "open"
        store.add(Order(id=i, customer=f"c{i}", status=status))
    return store


def test_get_returns_order_by_id():
    assert make_store(3).get(2) == Order(id=2, customer="c2", status="open")


def test_get_returns_none_when_missing():
    assert make_store(3).get(99) is None


def test_all_keeps_insertion_order():
    assert [o.id for o in make_store(3).all()] == [1, 2, 3]
