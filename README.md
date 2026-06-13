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
## Domains

**Primary domain:** AI & ML  ·  **JTF MERIDIAN division:** ATHENA-PRIME · SAGE

**Topics:** `cognis` `ai` `llm` `machine-learning` `python`

Part of the **Cognis Neural Suite** — 300+ source-available tools organized across 12 domains under the JTF MERIDIAN command structure. See the [suite on GitHub](https://github.com/cognis-digital) and [jtf-meridian](https://github.com/cognis-digital/jtf-meridian) for how the pieces fit together.
<!-- cognis:domains:end -->

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

## License

Cognis Open Collaboration License (COCL) 1.0 — source-available; free for
non-commercial use, commercial use requires a separate license. See
[LICENSE](LICENSE).
