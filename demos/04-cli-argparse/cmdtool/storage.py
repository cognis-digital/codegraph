"""Snapshot persistence."""


def save_snapshot(data):
    """Persist a snapshot and return its id (stubbed)."""
    return {"snapshot_id": "snap-001", "data": data}


def read_snapshot(snapshot_id):
    """Load a snapshot by id (stubbed)."""
    return {"snapshot_id": snapshot_id, "files": 3}
