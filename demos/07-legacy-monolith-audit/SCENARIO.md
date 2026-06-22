# Demo 07 — Auditing a messy legacy codebase (and surviving broken files)

## Where this came from
A legacy package with a grab-bag `core` utils module, a `report` module that
builds on it, and `broken_migration.py` — a half-finished migration script that
no longer parses. Real repos contain files like this; a fragile analyzer either
crashes or silently produces a wrong model. codegraph skips the unparseable
file and keeps going.

## The question you're answering
> *"Give me an honest inventory of this old package — and don't lie to me about
> the file that doesn't even parse."*

## Run it
```bash
cd demos/07-legacy-monolith-audit
codegraph build . --out codegraph.json

codegraph stats
codegraph search broken_migration     # prints nothing — it was skipped, not faked
codegraph callers func:legacy.core.retry
codegraph cycles                       # "no circular import dependencies found" (exit 0)
```

## What to expect
- `build` reports **8 nodes, 9 edges** across **3 modules** — `broken_migration`
  is absent because it failed to parse and was skipped (not mis-modeled).
- `search broken_migration` returns nothing, confirming the skip is honest.
- `callers` of `retry` shows `render_report` relies on the legacy retry helper.
- `cycles` reports none and exits 0 — a clean baseline you can wire into CI.

## How to act on it
This is the "is it safe to touch?" first pass on inherited code. The honest skip
behavior means counts you can trust; the `broken_migration.py` file is your
to-do list of things that don't even parse yet.
