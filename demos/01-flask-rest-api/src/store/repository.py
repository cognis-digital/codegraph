"""In-memory order repository (stand-in for a DB-backed one)."""


class OrderRepository:
    """CRUD over an in-memory order table."""

    def __init__(self):
        self._rows = {}
        self._next_id = 1

    def insert(self, row):
        """Insert a row, assigning an id."""
        row = dict(row, id=self._next_id)
        self._rows[self._next_id] = row
        self._next_id += 1
        return row

    def find(self, order_id):
        """Return the row with this id, or None."""
        return self._rows.get(order_id)

    def all(self):
        """Return every row."""
        return list(self._rows.values())
