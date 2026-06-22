# Demo 03 — "What does this nightly job actually do?"

## Where this came from
A small `etl` package with a single scheduler entry point, `run_pipeline`, that
orchestrates extract -> transform -> load across four modules. This is the data
job a new on-call engineer is paged about at 2am with no idea what it touches.

## The question you're answering
> *"The scheduler calls `run_pipeline` — what stages does it run, in what
> order, and which transforms are involved?"*

## Run it
```bash
cd demos/03-etl-pipeline
codegraph build . --out codegraph.json

# Top-down: what does the orchestrator call?
codegraph callees func:etl.pipeline.run_pipeline
#   -> func:etl.extract.fetch_rows
#   -> func:etl.transform.clean_rows
#   -> func:etl.transform.enrich_rows
#   -> func:etl.load.write_warehouse

# Drill into a stage
codegraph callees func:etl.transform.enrich_rows
#   -> func:etl.transform.region_for

# Picture it (paste into any Mermaid renderer / GitHub markdown)
codegraph mermaid --focus func:etl.pipeline.run_pipeline --depth 1
```

## What to expect
- `build` reports **12 nodes, 16 edges**.
- `callees` of `run_pipeline` lists all four stage functions.
- Drilling into `enrich_rows` shows it calls the private `region_for` helper.

## How to act on it
Use `callees` to reconstruct a runbook for an unfamiliar job, then attach the
focused Mermaid diagram to the runbook doc so the next on-call engineer sees the
DAG at a glance.
