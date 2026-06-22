# Demo 04 — Auto-documenting a CLI's command dispatch as a diagram

## Where this came from
A backup CLI (`cmdtool`) with an argparse front-end (`main.py`) that dispatches
to two subcommands, `snapshot` and `restore`, implemented in `commands.py` and
backed by `storage.py`. This is exactly the kind of tool whose README diagram
goes stale the day after it's drawn by hand.

## The question you're answering
> *"Give me an up-to-date architecture picture of how `main` dispatches the
> subcommands, generated from the real code — not hand-drawn."*

## Run it
```bash
cd demos/04-cli-argparse
codegraph build . --out codegraph.json

# Two hops out from the entry point, written to a Mermaid file
codegraph mermaid --focus func:cmdtool.main.main --depth 2 --out arch.mmd
cat arch.mmd
```

## What to expect
- `build` reports **11 nodes, 15 edges**.
- `arch.mmd` is a `graph LR` showing `main -> cmd_snapshot / cmd_restore`, each
  fanning out to its `collect_state`/`save_snapshot` and
  `read_snapshot`/`apply_state` helpers.
- Paste the `.mmd` body into any GitHub markdown fenced block tagged `mermaid`
  and it renders inline.

## How to act on it
Wire the `build ... && mermaid --out docs/arch.mmd` pair into CI so the diagram
is regenerated on every commit and never drifts from the code (see the repo's
top-level README, "Automate in CI").
