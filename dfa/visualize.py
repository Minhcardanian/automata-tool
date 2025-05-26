from graphviz import Digraph

def visualize_dfa(dfa, filename="dfa_graph", view=False, highlight_edges=None):
    """
    Render the given DFA to a PNG file using Graphviz.

    Parameters:
        dfa: instance of DFA with attributes states, transition, start_state, final_states
        filename: output filename (without extension)
        view: whether to open the image after rendering
        highlight_edges: optional list of (src_state, symbol) tuples to draw in red
    """
    dot = Digraph(format="png")
    dot.attr(rankdir="LR")

    # Draw start arrow
    dot.node("", shape="none")
    dot.edge("", dfa.start_state)

    # Draw states
    for state in dfa.states:
        shape = "doublecircle" if state in dfa.final_states else "circle"
        dot.node(state, shape=shape)

    # Draw transitions, highlighting if requested
    for src, transitions in dfa.transition.items():
        for symbol, dst in transitions.items():
            attrs = {}
            if highlight_edges and (src, symbol) in highlight_edges:
                attrs['color'] = 'red'
                attrs['penwidth'] = '2'
            dot.edge(src, dst, label=symbol, **attrs)

    # Render to file
    output_path = dot.render(filename, cleanup=True, view=view)
    print(f"[✓] DFA graph rendered to: {output_path}")
