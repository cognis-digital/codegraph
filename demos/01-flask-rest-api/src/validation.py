"""Request payload validation."""


def validate_order_payload(payload):
    """Raise ValueError on a malformed order payload; return it otherwise."""
    if "customer_id" not in payload:
        raise ValueError("customer_id is required")
    if not payload.get("items"):
        raise ValueError("items must be a non-empty list")
    return payload
