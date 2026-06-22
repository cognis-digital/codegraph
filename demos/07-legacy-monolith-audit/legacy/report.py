"""Reporting that builds on the core utilities."""

from legacy.core import parse_config, retry


def load_report_settings(text):
    """Parse report settings from a config blob."""
    return parse_config(text)


def render_report(fetch):
    """Render a report, retrying the fetch on transient failure."""
    data = retry(fetch)
    return {"rows": len(data)}
