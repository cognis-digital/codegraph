# A real legacy artifact: a half-finished migration script that no longer
# parses (note the dangling `def` with a syntax error). codegraph must SKIP it
# rather than crash or silently mis-model it.
def apply_migration(conn:
    cursor = conn.cursor(
    cursor.execute("ALTER TABLE orders ADD COLUMN region TEXT")
