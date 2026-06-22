# codegraph demos

Each folder is a self-contained, realistic mini-codebase in `codegraph`'s real
input format (a Python source tree) plus a `SCENARIO.md` that tells you where
the data came from, the exact commands to run, and what to expect. Every demo
has been run end to end — the node/edge counts in each `SCENARIO.md` are real.

Run any demo from its own directory after installing codegraph
(`pip install -e .` from the repo root), e.g.:

```bash
cd demos/01-flask-rest-api
codegraph build . --out codegraph.json
codegraph callees func:src.app.route_post_orders
```

(The generated `codegraph.json` / `*.mmd` outputs are gitignored — you create
them by running the demo.)

| # | Demo | What it shows | Key command |
|---|------|---------------|-------------|
| 01 | [flask-rest-api](01-flask-rest-api/) | Onboarding onto an unfamiliar service; pre-refactor blast radius | `search`, `callers`, `callees` |
| 02 | [import-cycle-billing](02-import-cycle-billing/) | Catching a latent 2-module circular import | `cycles`, `cycles --format json` |
| 03 | [etl-pipeline](03-etl-pipeline/) | Tracing what a nightly job orchestrates | `callees`, `mermaid` |
| 04 | [cli-argparse](04-cli-argparse/) | Auto-documenting CLI dispatch as a diagram | `mermaid --focus --depth` |
| 05 | [ml-training-loop](05-ml-training-loop/) | Grounded Q&A context over a training loop | `callees`, `assemble_context`, `ask` |
| 06 | [service-layer-cycle](06-service-layer-cycle/) | A hard-to-spot 3-module cycle (SCC) | `cycles`, `codegraph-emit` |
| 07 | [legacy-monolith-audit](07-legacy-monolith-audit/) | Honest audit that skips unparseable files | `stats`, `search`, `cycles` |

## The `cycles` command

Demos 02 and 06 exercise `codegraph cycles`, which reports circular import
dependencies among the codebase's own modules (computed as the non-trivial
strongly-connected components of the in-repo import graph). It exits non-zero
when cycles exist, so it works as a CI gate, and `--format json` emits findings
that flow straight into `codegraph-emit` / `cognis-connect`.
