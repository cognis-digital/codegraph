# Demo 01 — Onboarding onto an unfamiliar REST API

## Where this came from
A small order-management HTTP service (`src/`): an `app` routing layer, a
`service` business layer, a `validation` helper, and an in-memory `store`
repository. This is a realistic "you just joined the team, here is the
service" codebase.

## The question you're answering
> *"A request comes in to create an order — what code path actually runs, and
> who else calls the order-creation logic before I change it?"*

## Run it
```bash
cd demos/01-flask-rest-api
codegraph build . --out codegraph.json

# 1. What does the POST /orders handler actually call?
codegraph callees func:src.app.route_post_orders
#   -> func:src.service.create_order
#   -> func:src.validation.validate_order_payload

# 2. Before I touch create_order, who depends on it?
codegraph search create_order
codegraph callers func:src.service.create_order
#   -> func:src.app.route_post_orders   (only the POST route)

# 3. Sanity-check the shape of the codebase
codegraph stats
```

## What to expect
- `build` reports **21 nodes, 26 edges**.
- `callees` of the POST route shows it fans out to validation + the service.
- `callers` of `create_order` shows exactly one caller, so the blast radius of a
  change is small and well understood.

## How to act on it
Use `callers` as a pre-refactor blast-radius check and `callees` to trace a
request top-down. Pipe the JSON graph into a code-review bot or attach the
Mermaid export (see demo 04) to the PR that changes the handler.
