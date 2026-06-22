"""A grab-bag 'utils' module of the kind every legacy codebase accumulates."""


def parse_config(text):
    """Parse a key=value config blob into a dict."""
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        out[normalize_key(key)] = value.strip()
    return out


def normalize_key(key):
    """Lower-case and trim a config key."""
    return key.strip().lower()


def retry(fn, attempts=3):
    """Call `fn` up to `attempts` times, returning the first success."""
    last = None
    for _ in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - legacy catch-all
            last = exc
    raise last
