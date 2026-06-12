"""Grounded Q&A over a code knowledge graph using a local OpenAI-compatible backend.

``assemble_context`` is pure and testable: it selects the graph nodes most
relevant to a question and renders them as a compact context block (signatures,
docstrings, neighbors). ``ask`` sends that context to a backend -- by default
the Cognis coding fleet on :8772 -- so answers are grounded in the actual code,
not the model's imagination.
"""

from __future__ import annotations

import json
import urllib.request

from codegraph.graph import KnowledgeGraph

DEFAULT_BACKEND = "http://127.0.0.1:8772"
DEFAULT_MODEL = "coding"


def _degree(graph: KnowledgeGraph, node_id: str) -> int:
    return len(graph.neighbors(node_id))


def relevant_nodes(graph: KnowledgeGraph, question: str, k: int = 8) -> list[str]:
    """Pick up to ``k`` node ids most relevant to ``question``.

    Scoring: a node scores for each of its name's word-tokens that appears in the
    question (case-insensitive), with graph degree as a tie-breaker so central
    symbols win. Falls back to the highest-degree nodes when nothing matches.
    """
    q = question.lower()
    scored: list[tuple[int, int, str]] = []
    for node in graph.nodes.values():
        name_hit = node.name.lower() in q or any(
            tok and tok in q for tok in node.name.lower().replace("_", " ").split()
        )
        score = (2 if node.name.lower() in q else 1) if name_hit else 0
        scored.append((score, _degree(graph, node.id), node.id))
    scored.sort(reverse=True)
    top = [nid for score, _, nid in scored if score > 0][:k]
    if not top:  # nothing matched by name -> most central nodes
        top = [nid for _, _, nid in sorted(scored, key=lambda t: t[1], reverse=True)[:k]]
    return top


def assemble_context(graph: KnowledgeGraph, question: str, k: int = 8) -> str:
    """Render a compact, grounded context block for the relevant nodes."""
    blocks: list[str] = []
    for nid in relevant_nodes(graph, question, k):
        node = graph.nodes[nid]
        neigh = graph.neighbors(nid)[:6]
        doc = (node.doc or "").strip().splitlines()
        summary = doc[0] if doc else ""
        blocks.append(
            f"- {node.kind} {node.name}  ({node.file}:{node.lineno})\n"
            f"  id: {node.id}\n"
            + (f"  doc: {summary}\n" if summary else "")
            + (f"  connected: {', '.join(neigh)}\n" if neigh else "")
        )
    return "\n".join(blocks)


def ask(graph: KnowledgeGraph, question: str, backend: str = DEFAULT_BACKEND,
        model: str = DEFAULT_MODEL, k: int = 8, timeout: float = 120.0) -> str:
    """Answer ``question`` about the codebase, grounded in the graph.

    Sends the assembled context to an OpenAI-compatible ``backend``. Raises
    ``ConnectionError`` if the backend is unreachable.
    """
    context = assemble_context(graph, question, k)
    system = (
        "You answer questions about a codebase. Use ONLY the provided graph "
        "context (symbols, files, docstrings, connections). If the context is "
        "insufficient, say so plainly. Do not invent symbols."
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Question: {question}\n\nGraph context:\n{context}"},
        ],
        "temperature": 0.1,
    }
    req = urllib.request.Request(
        f"{backend.rstrip('/')}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
    except Exception as exc:
        raise ConnectionError(f"backend {backend} unreachable: {exc}") from exc
    return data["choices"][0]["message"]["content"]
