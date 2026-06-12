"""Tests for codegraph: AST extraction, queries, mermaid, persistence, context."""

import textwrap

import pytest

from codegraph.ask import assemble_context, relevant_nodes
from codegraph.build import build_graph
from codegraph.graph import KnowledgeGraph, Node


@pytest.fixture
def sample_repo(tmp_path):
    pkg = tmp_path / "sample"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "core.py").write_text(textwrap.dedent('''
        """Core module."""
        def helper(x):
            """Help with x."""
            return x + 1

        class Engine:
            """The engine."""
            def run(self):
                return helper(41)
    '''))
    (pkg / "app.py").write_text(textwrap.dedent('''
        from sample.core import Engine

        def main():
            """Entry point."""
            e = Engine()
            return e.run()
    '''))
    return str(tmp_path)


def test_build_extracts_modules_classes_functions(sample_repo):
    g = build_graph(sample_repo)
    kinds = {n.kind for n in g.nodes.values()}
    assert {"module", "class", "function"} <= kinds
    assert "class:sample.core.Engine" in g.nodes
    assert "func:sample.core.Engine.run" in g.nodes
    assert "func:sample.core.helper" in g.nodes


def test_defines_edges_link_module_to_symbols(sample_repo):
    g = build_graph(sample_repo)
    defined = {e.dst for e in g.out_edges("mod:sample.core", "defines")}
    assert "class:sample.core.Engine" in defined
    assert "func:sample.core.helper" in defined


def test_import_edges_only_kept_for_known_modules(sample_repo):
    g = build_graph(sample_repo)
    imports = g.imports_of("mod:sample.app")
    assert "mod:sample.core" in imports
    # an external import like "os" would not resolve to a node and is dropped
    assert all(dst in g.nodes for dst in imports)


def test_call_graph_is_resolved_by_name(sample_repo):
    g = build_graph(sample_repo)
    # Engine.run calls helper()
    assert "func:sample.core.helper" in g.callees("func:sample.core.Engine.run")
    # main() calls Engine() (constructor) and run()
    callees = g.callees("func:sample.app.main")
    assert "class:sample.core.Engine" in callees
    assert "func:sample.core.Engine.run" in callees


def test_callers_inverse_of_callees(sample_repo):
    g = build_graph(sample_repo)
    assert "func:sample.core.Engine.run" in g.callers("func:sample.core.helper")


def test_search_is_case_insensitive(sample_repo):
    g = build_graph(sample_repo)
    ids = {n.id for n in g.search("engine")}
    assert "class:sample.core.Engine" in ids


def test_stats_counts(sample_repo):
    s = build_graph(sample_repo).stats()
    assert s["nodes"] > 0 and s["edges"] > 0
    assert s["node:module"] >= 2


def test_save_load_roundtrip(sample_repo, tmp_path):
    g = build_graph(sample_repo)
    path = str(tmp_path / "g.json")
    g.save(path)
    reloaded = KnowledgeGraph.load(path)
    assert reloaded.stats() == g.stats()
    assert set(reloaded.nodes) == set(g.nodes)


def test_mermaid_focus_limits_to_neighborhood(sample_repo):
    g = build_graph(sample_repo)
    full = g.to_mermaid()
    focused = g.to_mermaid(focus="func:sample.core.helper", depth=1)
    assert focused.startswith("graph LR")
    assert len(focused) <= len(full)
    assert "helper" in focused


def test_syntax_errors_are_skipped(tmp_path):
    (tmp_path / "broken.py").write_text("def oops(:\n")
    (tmp_path / "ok.py").write_text("def fine():\n    return 1\n")
    g = build_graph(str(tmp_path))
    assert "func:ok.fine" in g.nodes
    assert not any("broken" in nid for nid in g.nodes)


def test_assemble_context_targets_relevant_nodes(sample_repo):
    g = build_graph(sample_repo)
    ctx = assemble_context(g, "what does the Engine do?")
    assert "Engine" in ctx
    # relevant_nodes always returns something, even with no name match
    assert relevant_nodes(g, "completely unrelated zzz") != []
