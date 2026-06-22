"""Auth service — needs the audit service to log logins.

Part of a three-module cycle: auth -> audit -> session -> auth. Larger
mutually-recursive clusters like this are harder to spot by eye than a simple
A<->B pair, which is exactly why an SCC-based detector earns its keep.
"""

from svc.audit import record_event


def login(user_id):
    """Authenticate a user and record the event."""
    record_event("login", user_id)
    return {"user_id": user_id, "ok": True}
