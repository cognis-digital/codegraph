"""Session service — re-authenticates expired sessions via auth.

This import back into `svc.auth` closes the three-module cycle.
"""

from svc.auth import login


def current_session(user_id):
    """Return the active session for a user, re-logging in if needed."""
    if not _has_session(user_id):
        login(user_id)
    return f"sess-{user_id}"


def _has_session(user_id):
    """Whether the user already has a live session (stubbed)."""
    return False
