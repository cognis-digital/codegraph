"""Load stage."""


def write_warehouse(dsn, rows):
    """Write rows to the warehouse and return the count (stubbed)."""
    return {"written": len(rows), "dsn": dsn}
