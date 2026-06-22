# Demo 06 — A three-module circular dependency (the hard kind to spot)

## Where this came from
A service layer where `auth` logs through `audit`, `audit` tags events with the
active `session`, and `session` re-authenticates via `auth` — a three-module
cycle (`auth -> audit -> session -> auth`). Pairwise A<->B cycles are easy to
notice in review; a three-hop cycle hides in plain sight. The detector finds it
because it computes strongly-connected components, not just back-edges.

## The question you're answering
> *"Is there a multi-module circular dependency in this service layer, and how
> bad is it?"*

## Run it
```bash
cd demos/06-service-layer-cycle
codegraph build . --out codegraph.json

codegraph cycles
#   cycle (3 modules): svc.audit, svc.auth, svc.session   (exit code 1)

codegraph cycles --format json
```

## What to expect
- `build` reports **8 nodes, 11 edges**.
- One finding covering all three modules. A 3+ module cluster is rated
  **medium** (vs. **high** for a tight 2-module cycle) — the size heuristic in
  `cycle_findings`.
- Exit code is **1**, so this can fail a CI job.

## How to act on it
Forward it straight into your alerting/ticketing via the bundled emit bridge:
```bash
codegraph cycles --format json | codegraph-emit --to webhook --url "$URL" --dry-run
```
Then break the loop by hoisting the shared contract (e.g. a `session_id` type)
into a dependency-free module the other three import.
