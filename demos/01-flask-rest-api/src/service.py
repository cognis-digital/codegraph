"""Order service layer — business logic, talks to the store."""

from src.store.repository import OrderRepository

_repo = OrderRepository()


def create_order(customer_id, items):
    """Persist a new order and return it."""
    total = compute_total(items)
    return _repo.insert({"customer_id": customer_id, "items": items, "total": total})


def get_order(order_id):
    """Fetch a single order by id, or None."""
    return _repo.find(order_id)


def list_orders():
    """Return all orders."""
    return _repo.all()


def compute_total(items):
    """Sum line-item prices."""
    return sum(i["price"] * i.get("qty", 1) for i in items)
