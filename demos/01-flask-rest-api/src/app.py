"""A small order-management REST API.

Thin HTTP layer that validates requests and delegates to the service layer.
This is the kind of codebase you point codegraph at on day one of a new job to
answer "where does an incoming request actually get handled?".
"""

from src.service import create_order, get_order, list_orders
from src.validation import validate_order_payload


class Request:
    """Minimal stand-in for a framework request object."""

    def __init__(self, json):
        self.json = json


def route_post_orders(request):
    """POST /orders — create a new order."""
    payload = validate_order_payload(request.json)
    order = create_order(payload["customer_id"], payload["items"])
    return {"status": 201, "order": order}


def route_get_order(order_id):
    """GET /orders/<id> — fetch one order."""
    order = get_order(order_id)
    if order is None:
        return {"status": 404}
    return {"status": 200, "order": order}


def route_get_orders():
    """GET /orders — list all orders."""
    return {"status": 200, "orders": list_orders()}
