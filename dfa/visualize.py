from graphviz import Digraph

def visualize_dfa(dfa, filename="dfa_graph", view=False, highlight_edges=None, highlight_nodes=None):
    """
    Render the given DFA to a PNG file using Graphviz.

    Parameters:
        dfa: instance of DFA with attributes states, transition, start_state, final_states
        filename: output filename (without extension)
        view: whether to open the image after rendering
        highlight_edges: optional list of (src_state, symbol) tuples to draw in red
        highlight_nodes: optional list of state names to fill with color
    """
    dot = Digraph(format="png")
    dot.attr(rankdir="LR")

    highlight_edges = highlight_edges or []
    highlight_nodes = set(highlight_nodes or [])

    # Draw start arrow
    dot.node("", shape="none")
    dot.edge("", dfa.start_state)

    # Draw states (doublecircle for finals, fill for current)
    for state in dfa.states:
        attrs = {}
        attrs['shape'] = "doublecircle" if state in dfa.final_states else "circle"
        if state in highlight_nodes:
            attrs['style'] = 'filled'
            attrs['fillcolor'] = 'lightpink'
        dot.node(state, **attrs)

    # Draw transitions (red + bold for highlighted edges)
    for src, transitions in dfa.transition.items():
        for symbol, dst in transitions.items():
            edge_attrs = {}
            if (src, symbol) in highlight_edges:
                edge_attrs['color'] = 'red'
                edge_attrs['penwidth'] = '2'
            dot.edge(src, dst, label=symbol, **edge_attrs)

    # Render to file
    output_path = dot.render(filename, cleanup=True, view=view)
    print(f"[✓] DFA graph rendered to: {output_path}")
