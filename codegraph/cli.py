"""codegraph CLI.

    codegraph build <path> [--out graph.json]    build the graph from a codebase
    codegraph stats [--graph graph.json]          node/edge counts
    codegraph search <query>                       find symbols by name
    codegraph callers <node_id>                    who calls this function
    codegraph callees <node_id>                    what this function calls
    codegraph cycles [--format json]               find circular import dependencies
    codegraph mermaid [--focus name --depth N]     export a Mermaid diagram
    codegraph ask "<question>" [--backend URL]      grounded Q&A via the coding fleet

The graph defaults to ./codegraph.json (override with --graph / --out).
"""

from __future__ import annotations

import argparse
import sys

from codegraph.ask import DEFAULT_BACKEND, DEFAULT_MODEL, ask
from codegraph.build import build_graph
from codegraph.graph import KnowledgeGraph

DEFAULT_GRAPH = "codegraph.json"


def _load(path: str) -> KnowledgeGraph:
    try:
        return KnowledgeGraph.load(path)
    except FileNotFoundError:
        print(f"no graph at {path}; run 'codegraph build <path>' first", file=sys.stderr)
        raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="codegraph", description=__doc__.splitlines()[0])
    parser.add_argument("--graph", default=DEFAULT_GRAPH, help=f"graph file (default: {DEFAULT_GRAPH})")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="build a graph from a codebase")
    p_build.add_argument("path")
    p_build.add_argument("--out", default=DEFAULT_GRAPH)

    sub.add_parser("stats", help="show node/edge counts")

    p_search = sub.add_parser("search", help="find symbols by name")
    p_search.add_argument("query")

    p_callers = sub.add_parser("callers", help="functions that call a node")
    p_callers.add_argument("node_id")

    p_callees = sub.add_parser("callees", help="functions a node calls")
    p_callees.add_argument("node_id")

    p_cycles = sub.add_parser("cycles", help="find circular import dependencies")
    p_cycles.add_argument("--format", choices=["text", "json"], default="text",
                          help="'json' emits findings consumable by codegraph-emit")

    p_merm = sub.add_parser("mermaid", help="export a Mermaid diagram")
    p_merm.add_argument("--focus", default=None)
    p_merm.add_argument("--depth", type=int, default=1)
    p_merm.add_argument("--out", default=None)

    p_ask = sub.add_parser("ask", help="grounded Q&A over the codebase")
    p_ask.add_argument("question")
    p_ask.add_argument("--backend", default=DEFAULT_BACKEND)
    p_ask.add_argument("--model", default=DEFAULT_MODEL)

    args = parser.parse_args(argv)

    if args.command == "build":
        graph = build_graph(args.path)
        graph.save(args.out)
        s = graph.stats()
        print(f"built {args.out}: {s['nodes']} nodes, {s['edges']} edges")
        return 0

    if args.command == "stats":
        for key, value in _load(args.graph).stats().items():
            print(f"{key}\t{value}")
        return 0

    if args.command == "search":
        for node in _load(args.graph).search(args.query):
            print(f"{node.id}\t({node.file}:{node.lineno})")
        return 0

    if args.command == "callers":
        for nid in _load(args.graph).callers(args.node_id):
            print(nid)
        return 0

    if args.command == "callees":
        for nid in _load(args.graph).callees(args.node_id):
            print(nid)
        return 0

    if args.command == "cycles":
        graph = _load(args.graph)
        if args.format == "json":
            import json
            print(json.dumps({"findings": graph.cycle_findings()}, indent=2))
            return 0
        cycles = graph.import_cycles()
        if not cycles:
            print("no circular import dependencies found")
            return 0
        for cluster in cycles:
            names = [graph.nodes[m].name if m in graph.nodes else m for m in cluster]
            print(f"cycle ({len(cluster)} modules): {', '.join(names)}")
        # non-zero exit so CI can gate on "no new import cycles"
        return 1

    if args.command == "mermaid":
        text = _load(args.graph).to_mermaid(focus=args.focus, depth=args.depth)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as handle:
                handle.write(text)
            print(f"wrote {args.out}")
        else:
            print(text)
        return 0

    if args.command == "ask":  # pragma: no cover  (needs a live backend)
        try:
            print(ask(_load(args.graph), args.question, backend=args.backend, model=args.model))
        except ConnectionError as exc:
            print(exc, file=sys.stderr)
            return 1
        return 0

    return 0  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
