"""codegraph -- turn any Python codebase into a queryable knowledge graph you can
explore, search, diagram, and ask questions about (grounded via the Cognis fleet)."""

from codegraph.ask import ask, assemble_context, relevant_nodes
from codegraph.build import build_graph
from codegraph.graph import Edge, KnowledgeGraph, Node

__version__ = "0.1.0"

__all__ = [
    "KnowledgeGraph",
    "Node",
    "Edge",
    "build_graph",
    "ask",
    "assemble_context",
    "relevant_nodes",
    "__version__",
]
