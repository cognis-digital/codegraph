"""Build a knowledge graph from a Python codebase using the ``ast`` module.

Extraction is exact for structure (modules, classes, functions, imports) and
best-effort for calls: a ``calls`` edge is added when a called name resolves to
a function/method defined somewhere in the same codebase. Cross-file calls are
matched by short name, so the call graph is a strong hint, not a proof — this is
stated plainly rather than overclaimed.
"""

from __future__ import annotations

import ast
import os

from codegraph.graph import KnowledgeGraph, Node

SKIP_DIRS = {".git", ".venv", "venv", "env", "__pycache__", "node_modules", "build", "dist", ".tox"}


def _module_id(root: str, path: str) -> str:
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    if rel.endswith(".py"):
        rel = rel[:-3]
    if rel.endswith("/__init__"):
        rel = rel[: -len("/__init__")]
    return rel.replace("/", ".")


def _iter_py_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".py"):
                yield os.path.join(dirpath, name)


def build_graph(root: str) -> KnowledgeGraph:
    """Parse every ``*.py`` under ``root`` into a KnowledgeGraph."""
    graph = KnowledgeGraph()
    # Pass 1: nodes + structural edges; collect short-name -> function-node-id map.
    func_by_name: dict[str, list[str]] = {}
    pending_calls: list[tuple[str, set[str]]] = []

    for path in sorted(_iter_py_files(root)):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        mod_id_str = _module_id(root, path)
        try:
            tree = ast.parse(open(path, encoding="utf-8", errors="replace").read(), filename=path)
        except SyntaxError:
            continue
        mod_node_id = f"mod:{mod_id_str}"
        graph.add_node(Node(mod_node_id, "module", mod_id_str, rel, 1, ast.get_docstring(tree) or ""))

        for node in tree.body:
            _walk_top(node, graph, mod_id_str, mod_node_id, rel, func_by_name, pending_calls, prefix="")

        # imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    graph.add_edge(mod_node_id, f"mod:{alias.name}", "imports")
            elif isinstance(node, ast.ImportFrom) and node.module:
                graph.add_edge(mod_node_id, f"mod:{node.module}", "imports")

    # keep only import edges that point at modules we actually have
    graph.edges = [
        e for e in graph.edges
        if e.kind != "imports" or e.dst in graph.nodes
    ]

    # Pass 2: resolve calls by short name.
    for caller_id, called_names in pending_calls:
        for name in called_names:
            for target_id in func_by_name.get(name, []):
                if target_id != caller_id:
                    graph.add_edge(caller_id, target_id, "calls")
    return graph


def _walk_top(node, graph, mod_id_str, parent_id, rel, func_by_name, pending_calls, prefix):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        qual = f"{prefix}{node.name}" if prefix else node.name
        fid = f"func:{mod_id_str}.{qual}"
        graph.add_node(Node(fid, "function", node.name, rel, node.lineno, ast.get_docstring(node) or ""))
        graph.add_edge(parent_id, fid, "defines")
        func_by_name.setdefault(node.name, []).append(fid)
        pending_calls.append((fid, _called_names(node)))
    elif isinstance(node, ast.ClassDef):
        cid = f"class:{mod_id_str}.{prefix}{node.name}"
        graph.add_node(Node(cid, "class", node.name, rel, node.lineno, ast.get_docstring(node) or ""))
        graph.add_edge(parent_id, cid, "defines")
        # constructor calls (ClassName(...)) resolve like a function of the class name
        func_by_name.setdefault(node.name, []).append(cid)
        for child in node.body:
            _walk_top(child, graph, mod_id_str, cid, rel, func_by_name, pending_calls, prefix=f"{node.name}.")


def _called_names(func_node) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                names.add(func.attr)
    return names
