from __future__ import annotations

from pathlib import Path

from dfa.dfa import DFA
from dfa.visualize import visualize_dfa


def render_graph(
    dfa: DFA,
    graph_path: str | Path,
    highlight_edges: list[tuple[str, str]] | None = None,
    highlight_nodes: list[str] | None = None,
) -> None:
    graph_path = Path(graph_path)
    visualize_dfa(
        dfa,
        view=False,
        filename=str(graph_path.with_suffix("")),
        highlight_edges=highlight_edges,
        highlight_nodes=highlight_nodes,
    )
