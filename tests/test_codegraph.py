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


# --- import-cycle detection ---------------------------------------------

@pytest.fixture
def cyclic_repo(tmp_path):
    """A package with a 2-module cycle (a<->b) and an acyclic c."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "a.py").write_text("from pkg.b import bee\ndef a():\n    return bee()\n")
    (pkg / "b.py").write_text("from pkg.a import a\ndef bee():\n    return a()\n")
    (pkg / "c.py").write_text("from pkg.a import a\ndef c():\n    return a()\n")
    return str(tmp_path)


def test_import_cycles_finds_two_module_cycle(cyclic_repo):
    g = build_graph(cyclic_repo)
    cycles = g.import_cycles()
    assert cycles == [["mod:pkg.a", "mod:pkg.b"]]
    # c imports a but isn't imported back -> not in any cycle
    assert all("mod:pkg.c" not in c for c in cycles)


def test_import_cycles_none_when_acyclic(sample_repo):
    # sample_repo: app imports core, but core never imports app
    assert build_graph(sample_repo).import_cycles() == []


def test_import_cycles_finds_three_module_scc(tmp_path):
    pkg = tmp_path / "svc"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "x.py").write_text("from svc.y import y\ndef x():\n    return y()\n")
    (pkg / "y.py").write_text("from svc.z import z\ndef y():\n    return z()\n")
    (pkg / "z.py").write_text("from svc.x import x\ndef z():\n    return x()\n")
    cycles = build_graph(str(tmp_path)).import_cycles()
    assert cycles == [["mod:svc.x", "mod:svc.y", "mod:svc.z"]]


def test_cycle_findings_shape_and_severity(cyclic_repo, tmp_path):
    g = build_graph(cyclic_repo)
    findings = g.cycle_findings()
    assert len(findings) == 1
    f = findings[0]
    assert f["type"] == "import-cycle"
    assert f["severity"] == "high"          # a tight 2-module cycle
    assert set(f["modules"]) == {"mod:pkg.a", "mod:pkg.b"}
    assert "import-cycle" in f["tags"]
    assert sorted(f["files"]) == ["pkg/a.py", "pkg/b.py"]


def test_cycle_findings_three_module_is_medium(tmp_path):
    root = tmp_path / "proj"
    pkg = root / "svc"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "x.py").write_text("from svc.y import y\n")
    (pkg / "y.py").write_text("from svc.z import z\n")
    (pkg / "z.py").write_text("from svc.x import x\n")
    findings = build_graph(str(root)).cycle_findings()
    assert len(findings) == 1
    assert findings[0]["severity"] == "medium"
    assert len(findings[0]["modules"]) == 3


def test_cli_cycles_exit_codes(tmp_path, capsys):
    from codegraph.cli import main

    # cyclic project in its own root
    cyc_root = tmp_path / "cyc_proj"
    pkg = cyc_root / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "a.py").write_text("from pkg.b import bee\ndef a():\n    return bee()\n")
    (pkg / "b.py").write_text("from pkg.a import a\ndef bee():\n    return a()\n")
    cyc_graph = str(tmp_path / "cyc.json")
    build_graph(str(cyc_root)).save(cyc_graph)
    assert main(["--graph", cyc_graph, "cycles"]) == 1          # cycles -> nonzero
    assert "cycle" in capsys.readouterr().out

    # acyclic project in a separate root
    clean_root = tmp_path / "clean_proj"
    sp = clean_root / "sample"
    sp.mkdir(parents=True)
    (sp / "__init__.py").write_text("")
    (sp / "core.py").write_text("def helper(x):\n    return x + 1\n")
    (sp / "app.py").write_text("from sample.core import helper\ndef main():\n    return helper(1)\n")
    clean_graph = str(tmp_path / "clean.json")
    build_graph(str(clean_root)).save(clean_graph)
    assert main(["--graph", clean_graph, "cycles"]) == 0        # none -> zero
    assert "no circular import" in capsys.readouterr().out


def test_cli_cycles_json_format(tmp_path, capsys):
    import json
    from codegraph.cli import main

    root = tmp_path / "proj"
    pkg = root / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "a.py").write_text("from pkg.b import bee\ndef a():\n    return bee()\n")
    (pkg / "b.py").write_text("from pkg.a import a\ndef bee():\n    return a()\n")
    g = str(tmp_path / "cyc.json")
    build_graph(str(root)).save(g)
    main(["--graph", g, "cycles", "--format", "json"])
    out = json.loads(capsys.readouterr().out)
    assert out["findings"][0]["type"] == "import-cycle"
