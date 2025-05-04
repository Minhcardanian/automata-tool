from graphviz import Digraph

def visualize_dfa(dfa, filename="dfa_graph", view=False):
    dot = Digraph(format="png")
    dot.attr(rankdir="LR")

    # Draw start arrow
    dot.node("", shape="none")
    dot.edge("", dfa.start_state)

    # Draw states
    for state in dfa.states:
        shape = "doublecircle" if state in dfa.final_states else "circle"
        dot.node(state, shape=shape)

    # Draw transitions
    for src, transitions in dfa.transition.items():
        for symbol, dst in transitions.items():
            dot.edge(src, dst, label=symbol)

    output_path = dot.render(filename, cleanup=True, view=view)
    print(f"[✓] DFA graph rendered to: {output_path}")
