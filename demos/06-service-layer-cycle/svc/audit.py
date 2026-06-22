"""Audit service — annotates events with the current session."""

from svc.session import current_session


def record_event(kind, user_id):
    """Record an audited event, tagged with the active session."""
    session = current_session(user_id)
    return {"kind": kind, "user_id": user_id, "session": session}
