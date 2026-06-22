"""The knowledge-graph data model and queries.

A codebase becomes a graph of **nodes** (modules, classes, functions) connected
by **edges** (``defines``, ``imports``, ``calls``). The graph is plain data:
JSON-serializable, queryable without any network, and exportable to Mermaid for
an at-a-glance picture.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections import defaultdict
from dataclasses import asdict, dataclass, field


@dataclass
class Node:
    id: str
    kind: str  # "module" | "class" | "function"
    name: str
    file: str
    lineno: int = 0
    doc: str = ""


@dataclass
class Edge:
    src: str
    dst: str
    kind: str  # "defines" | "imports" | "calls"


@dataclass
class KnowledgeGraph:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)

    # --- construction ----------------------------------------------------
    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def add_edge(self, src: str, dst: str, kind: str) -> None:
        self.edges.append(Edge(src, dst, kind))

    # --- queries ---------------------------------------------------------
    def search(self, query: str) -> list[Node]:
        """Nodes whose name or id contains ``query`` (case-insensitive)."""
        q = query.lower()
        hits = [n for n in self.nodes.values() if q in n.name.lower() or q in n.id.lower()]
        return sorted(hits, key=lambda n: n.id)

    def out_edges(self, node_id: str, kind: str | None = None) -> list[Edge]:
        return [e for e in self.edges if e.src == node_id and (kind is None or e.kind == kind)]

    def in_edges(self, node_id: str, kind: str | None = None) -> list[Edge]:
        return [e for e in self.edges if e.dst == node_id and (kind is None or e.kind == kind)]

    def neighbors(self, node_id: str) -> list[str]:
        """All directly connected node ids (either direction)."""
        out = {e.dst for e in self.edges if e.src == node_id}
        inc = {e.src for e in self.edges if e.dst == node_id}
        return sorted(out | inc)

    def callees(self, node_id: str) -> list[str]:
        """Functions called by ``node_id``."""
        return sorted({e.dst for e in self.out_edges(node_id, "calls")})

    def callers(self, node_id: str) -> list[str]:
        """Functions that call ``node_id``."""
        return sorted({e.src for e in self.in_edges(node_id, "calls")})

    def imports_of(self, module_id: str) -> list[str]:
        return sorted({e.dst for e in self.out_edges(module_id, "imports")})

    def import_cycles(self) -> list[list[str]]:
        """Detect circular import dependencies among the codebase's own modules.

        Returns each circular-dependency cluster as a list of module ids, e.g.
        ``["mod:a", "mod:b"]`` for ``a -> b -> a``. Clusters are the non-trivial
        strongly-connected components of the in-repo import graph (a module that
        imports itself counts too), so every reported group is a real, mutual
        circular dependency rather than a one-way edge.

        Only edges that stay inside this graph count (third-party imports are
        already dropped at build time). Each cluster is sorted, and the list of
        clusters is sorted, so the result is deterministic and stable across
        runs and platforms.
        """
        adj: dict[str, list[str]] = defaultdict(list)
        nodes: set[str] = set()
        for edge in self.edges:
            if edge.kind == "imports" and edge.src in self.nodes and edge.dst in self.nodes:
                nodes.add(edge.src)
                nodes.add(edge.dst)
                if edge.dst not in adj[edge.src]:
                    adj[edge.src].append(edge.dst)
        for targets in adj.values():
            targets.sort()

        # Tarjan's strongly-connected-components (iterative; recursion-safe).
        index_of: dict[str, int] = {}
        low: dict[str, int] = {}
        on_stack: set[str] = set()
        stack: list[str] = []
        counter = 0
        sccs: list[list[str]] = []

        for root in sorted(nodes):
            if root in index_of:
                continue
            work: list[tuple[str, int]] = [(root, 0)]
            while work:
                v, pi = work[-1]
                if pi == 0:
                    index_of[v] = low[v] = counter
                    counter += 1
                    stack.append(v)
                    on_stack.add(v)
                recursed = False
                neigh = adj.get(v, ())
                while pi < len(neigh):
                    w = neigh[pi]
                    if w not in index_of:
                        work[-1] = (v, pi + 1)
                        work.append((w, 0))
                        recursed = True
                        break
                    if w in on_stack:
                        low[v] = min(low[v], index_of[w])
                    pi += 1
                if recursed:
                    continue
                if low[v] == index_of[v]:
                    comp: list[str] = []
                    while True:
                        w = stack.pop()
                        on_stack.discard(w)
                        comp.append(w)
                        if w == v:
                            break
                    sccs.append(sorted(comp))
                work.pop()
                if work:
                    parent = work[-1][0]
                    low[parent] = min(low[parent], low[v])

        cycles = [c for c in sccs if len(c) > 1 or c[0] in adj.get(c[0], ())]
        return sorted(cycles)

    def cycle_findings(self) -> list[dict]:
        """Import cycles rendered as JSON findings (for ``codegraph-emit``)."""
        findings = []
        for cluster in self.import_cycles():
            mods = [self.nodes[m].name if m in self.nodes else m for m in cluster]
            group = ", ".join(mods)
            files = sorted({self.nodes[m].file for m in cluster if m in self.nodes})
            findings.append({
                "type": "import-cycle",
                "title": f"Circular import among: {group}",
                # a tight 2-module cycle is the most urgent to break; larger
                # mutually-recursive clusters are medium.
                "severity": "high" if len(cluster) == 2 else "medium",
                "description": (
                    f"{len(cluster)} module(s) form a circular import dependency "
                    f"({group}). Circular imports couple modules tightly, can "
                    f"raise ImportError depending on load order, and block clean "
                    f"refactoring. Break the cycle by extracting the shared "
                    f"symbols into a third module or using a local/deferred import."
                ),
                "modules": list(cluster),
                "tags": ["code-health", "import-cycle", "maintainability"],
                "files": files,
            })
        return findings

    def stats(self) -> dict[str, int]:
        kinds: dict[str, int] = defaultdict(int)
        for node in self.nodes.values():
            kinds[node.kind] += 1
        edge_kinds: dict[str, int] = defaultdict(int)
        for edge in self.edges:
            edge_kinds[edge.kind] += 1
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            **{f"node:{k}": v for k, v in sorted(kinds.items())},
            **{f"edge:{k}": v for k, v in sorted(edge_kinds.items())},
        }

    # --- export ----------------------------------------------------------
    def to_mermaid(self, focus: str | None = None, depth: int = 1) -> str:
        """Render (a neighborhood of) the graph as a Mermaid ``graph LR``."""
        if focus is None:
            include = set(self.nodes)
        else:
            include = {focus}
            frontier = {focus}
            for _ in range(max(depth, 0)):
                nxt: set[str] = set()
                for nid in frontier:
                    nxt.update(self.neighbors(nid))
                include |= nxt
                frontier = nxt
        lines = ["graph LR"]
        seen_edge = set()
        for edge in self.edges:
            if edge.src in include and edge.dst in include:
                key = (edge.src, edge.dst, edge.kind)
                if key in seen_edge:
                    continue
                seen_edge.add(key)
                lines.append(f'  {_mid(edge.src)}["{_label(self, edge.src)}"] '
                             f'-->|{edge.kind}| {_mid(edge.dst)}["{_label(self, edge.dst)}"]')
        return "\n".join(lines)

    # --- persistence -----------------------------------------------------
    def to_dict(self) -> dict:
        return {"nodes": [asdict(n) for n in self.nodes.values()],
                "edges": [asdict(e) for e in self.edges]}

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeGraph":
        graph = cls()
        for n in data.get("nodes", []):
            graph.add_node(Node(**n))
        for e in data.get("edges", []):
            graph.edges.append(Edge(**e))
        return graph

    def save(self, path: str) -> None:
        directory = os.path.dirname(os.path.abspath(path))
        os.makedirs(directory, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(self.to_dict(), handle, indent=2, sort_keys=True)
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    @classmethod
    def load(cls, path: str) -> "KnowledgeGraph":
        with open(path, encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))


def _mid(node_id: str) -> str:
    """A Mermaid-safe node identifier."""
    return "n_" + "".join(c if c.isalnum() else "_" for c in node_id)


def _label(graph: KnowledgeGraph, node_id: str) -> str:
    node = graph.nodes.get(node_id)
    return node.name if node else node_id
