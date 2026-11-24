import pytest

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


def test_page_returns_at_most_page_size_orders():
    assert len(make_store(50).page(1, page_size=10)) == 10


def test_page_leaves_out_cancelled_orders():
    page = make_store(50, cancelled_every=5).page(1, page_size=10)
    assert all(o.status != "cancelled" for o in page)


def test_page_rejects_page_zero():
    with pytest.raises(ValueError):
        make_store(5).page(0)
