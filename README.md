# codegraph

**Turn any Python codebase into a queryable knowledge graph you can explore, search, diagram, and ask questions about — grounded in the real code.**

Point `codegraph` at a project and it parses every module into a graph of
**modules, classes, and functions** linked by **defines / imports / calls**
edges. Then you can search symbols, trace who-calls-what, export a Mermaid map,
or ask a natural-language question that's answered *from the graph* by your local
Cognis coding fleet — so the answer is grounded in the actual code, not guessed.

Pure standard library for everything except `ask` (which talks to an
OpenAI-compatible backend over HTTP). Runs anywhere Python 3.10+ runs.

<!-- cognis:domains:start -->

<!-- cognis:example:start -->
## 🔎 Example output

Real, reproducible output from the tool — runs offline:

```console
$ codegraph-emit --help
usage: codegraph-emit [-h]
                      --to {stix,taxii,misp,sigma,splunk,elastic,slack,discord,webhook,brief,findings}
                      [--url URL] [--token TOKEN] [--dry-run]
                      [input]

forward codegraph JSON findings to a platform via cognis-connect

positional arguments:
  input                 findings JSON file (default: stdin)

options:
  -h, --help            show this help message and exit
  --to {stix,taxii,misp,sigma,splunk,elastic,slack,discord,webhook,brief,findings}
  --url URL
  --token TOKEN
  --dry-run
```

> Blocks above are real `codegraph` output — reproduce them from a clone.

**Sample result format** _(illustrative values — run on your own data for real findings):_

```
{
  "codeGraph": {
    "id": "1234567890",
    "name": "Example Code Graph",
    "description": "This is an example code graph.",
    "findings": [
      {
        "id": "1",
        "title": "Example Finding 1",
        "category": "example_category",
        "severity": "high"
      },
      {
        "id": "2",
        "title": "Example Finding 2",
        "category": "another_example_category",
        "severity": "medium"
      }
    ]
  }
}
```

<!-- cognis:example:end -->

## Domains

**Primary domain:** AI & ML  ·  **JTF MERIDIAN division:** ATHENA-PRIME · SAGE

**Topics:** `cognis` `ai` `llm` `machine-learning` `python`

Part of the **Cognis Neural Suite** — 300+ source-available tools organized across 12 domains under the JTF MERIDIAN command structure. See the [suite on GitHub](https://github.com/cognis-digital) and [jtf-meridian](https://github.com/cognis-digital/jtf-meridian) for how the pieces fit together.
<!-- cognis:domains:end -->

## Usage — step by step

`codegraph` parses a Python project into a graph of modules/classes/functions linked by defines/imports/calls edges, then lets you query it.

1. **Install** (Python 3.10+):
   ```bash
   pip install "git+https://github.com/cognis-digital/codegraph.git"
   ```
2. **Build the graph** from a codebase (defaults to `./codegraph.json`):
   ```bash
   codegraph build ./myproject --out codegraph.json
   ```
3. **Explore it** — counts, symbol search, and call relationships:
   ```bash
   codegraph stats
   codegraph search Engine
   codegraph callers func:pkg.mod.helper   # who calls this
   codegraph callees func:pkg.mod.main     # what it calls
   ```
4. **Check code health** — find circular import dependencies (exits non-zero when any exist, so it doubles as a CI gate):
   ```bash
   codegraph cycles                # human-readable
   codegraph cycles --format json  # findings for a SIEM / ticket / cognis-connect
   ```
5. **Use the output** — export a Mermaid diagram (stdout or `--out`), or ask a graph-grounded question via your local coding fleet on `:8772` (override with `--backend`/`--model`):
   ```bash
   codegraph mermaid --focus func:pkg.mod.run --depth 1 --out graph.mmd
   codegraph ask "how does request routing resolve a model?"
   ```
6. **Automate in CI** — rebuild on each commit, fail on new import cycles, and publish the diagram:
   ```bash
   codegraph build . --out codegraph.json
   codegraph cycles                       # non-zero exit fails the build on a new cycle
   codegraph mermaid --out docs/arch.mmd
   ```

## Worked examples

The [`demos/`](demos/) directory has seven self-contained, realistic
mini-codebases — a REST API, an ETL pipeline, a CLI tool, an ML training loop,
two flavors of circular-import bug, and a messy legacy package — each with a
`SCENARIO.md` giving the exact commands and expected output. Every demo has
been run end to end. Start with [`demos/README.md`](demos/README.md).

## Install

```bash
pip install "git+https://github.com/cognis-digital/codegraph.git"
```

## Use

```bash
codegraph build ./myproject            # -> codegraph.json
codegraph stats
codegraph search Engine                # find symbols by name
codegraph callers func:pkg.mod.helper  # who calls this?
codegraph callees func:pkg.mod.main    # what does it call?
codegraph cycles                       # circular import dependencies (CI-gateable)
codegraph mermaid --focus func:pkg.mod.run --depth 1 --out graph.mmd
codegraph ask "how does request routing resolve a model?"
```

`ask` sends a compact, graph-derived context block (relevant symbols, their
docstrings, and their connections) to the Cognis coding fleet on `:8772` by
default; override with `--backend http://host:port --model <name>` to use any
OpenAI-compatible endpoint (including [edgemesh](https://github.com/cognis-digital/edgemesh)).

## As a library

```python
from codegraph.build import build_graph
from codegraph.ask import ask

graph = build_graph("./myproject")
graph.save("codegraph.json")
print(ask(graph, "what calls the schema validator?"))
```

## How accurate is it?

- **Structure** (modules, classes, functions, imports) is exact, from Python's
  `ast`.
- **Call edges** are best-effort: a `calls` edge is added when a called name
  resolves to a function/method/class defined *somewhere in the same codebase*,
  matched by short name. It's a strong navigational hint, not a sound
  inter-procedural analysis — stated plainly rather than overclaimed.
- Files that don't parse are skipped (not silently mis-modeled).

## Relationship to other tools

The "codebase as an explorable knowledge graph" idea is a good one and not
unique to this project. `codegraph` is an **original, clean-room** implementation
— it ships no third-party code — designed to plug into the Cognis fleet and to
produce context that any agent (Claude Code, Codex, Cursor, Copilot, …) can
consume.

## Interoperability

`codegraph` composes with the 300+ tool Cognis suite — JSON in/out and a shared
OpenAI-compatible `/v1` backbone. See **[INTEROP.md](INTEROP.md)** for the
suite map, composition patterns, and reference stacks.

## Integrations

Forward `codegraph`'s findings to STIX/MISP/Sigma/Splunk/Elastic/Slack/webhooks via
[`cognis-connect`](https://github.com/cognis-digital/cognis-connect). See **[INTEGRATIONS.md](INTEGRATIONS.md)**.

## License

Cognis Open Collaboration License (COCL) 1.0 — source-available; free for
non-commercial use, commercial use requires a separate license. See
[LICENSE](LICENSE).
