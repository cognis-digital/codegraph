"""Subcommand implementations."""

from cmdtool.storage import read_snapshot, save_snapshot


def cmd_snapshot():
    """Take a new snapshot of the working set."""
    data = collect_state()
    return save_snapshot(data)


def cmd_restore(snapshot_id):
    """Restore the working set from a snapshot id."""
    data = read_snapshot(snapshot_id)
    return apply_state(data)


def collect_state():
    """Gather the current state to snapshot (stubbed)."""
    return {"files": 3}


def apply_state(data):
    """Apply a restored state (stubbed)."""
    return {"restored": data}
