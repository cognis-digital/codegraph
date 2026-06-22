"""Nightly ETL orchestrator: extract -> transform -> load.

`run_pipeline` is the single entry point a scheduler (cron, Airflow, etc.)
invokes. Tracing what it orchestrates is the canonical "what does this job
actually do?" question for a data team.
"""

from etl.extract import fetch_rows
from etl.load import write_warehouse
from etl.transform import clean_rows, enrich_rows


def run_pipeline(source_url, warehouse_dsn):
    """Run the full nightly job end to end."""
    raw = fetch_rows(source_url)
    cleaned = clean_rows(raw)
    enriched = enrich_rows(cleaned)
    return write_warehouse(warehouse_dsn, enriched)
