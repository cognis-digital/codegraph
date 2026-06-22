# Demo 02 — Catching a circular import before it bites in prod

## Where this came from
A `billing` package with two models, `invoice.py` and `customer.py`, that import
each other at module scope. The app boots fine today purely because of the
order the modules happen to load — exactly the kind of latent bug that surfaces
as a mysterious `ImportError` after an unrelated refactor reorders imports.

## The question you're answering
> *"Does this codebase have any circular import dependencies, and which files
> do I need to untangle?"*

## Run it (uses the `cycles` feature)
```bash
cd demos/02-import-cycle-billing
codegraph build . --out codegraph.json

# Human-readable; exits non-zero so CI can gate on it
codegraph cycles
#   cycle (2 modules): billing.customer, billing.invoice

# Machine-readable findings for a SIEM / ticket / cognis-connect
codegraph cycles --format json
```

## What to expect
- `codegraph cycles` prints the two-module cycle and **exits with status 1**
  (so `codegraph cycles` can be a CI gate that fails the build on a new cycle).
- `--format json` emits a `findings` array. A tight 2-module cycle is rated
  **high** severity (it's the most urgent to break); larger mutually-recursive
  clusters are rated medium.

## How to act on it
Break the cycle: move the shared type into a third module, or defer one import
into the function that needs it (`def open_invoice(...): from billing.invoice
import Invoice`). Forward the JSON findings to a ticket tracker or any platform:

```bash
codegraph cycles --format json | codegraph-emit --to slack --url "$WEBHOOK" --dry-run
```
