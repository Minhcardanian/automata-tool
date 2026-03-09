from __future__ import annotations

from dfa.dfa import DFA
from nfa.nfa import EPSILON, NFA


def epsilon_closure(nfa: NFA, states: set[str]) -> set[str]:
    """Backward-compatible wrapper around NFA-owned epsilon-closure."""
    return nfa.epsilon_closure(states)


def move(nfa: NFA, states: set[str], symbol: str) -> set[str]:
    result: set[str] = set()
    for state in states:
        result.update(nfa.transition.get(state, {}).get(symbol, set()))
    return result


def nfa_to_dfa(nfa: NFA) -> DFA:
    """Convert NFA (with optional ε-transitions) to a total DFA."""
    start_closure = nfa.epsilon_closure({nfa.start_state})
    unmarked = [frozenset(start_closure)]
    dfa_states: set[str] = set()
    dfa_transitions: dict[str, dict[str, str]] = {}
    dfa_final_states: set[str] = set()
    state_map: dict[frozenset[str], str] = {}
    state_count = 0

    symbols = sorted(sym for sym in nfa.alphabet if sym != EPSILON)

    while unmarked:
        current = unmarked.pop()
        if current not in state_map:
            state_map[current] = f"S{state_count}"
            state_count += 1

        current_name = state_map[current]
        dfa_states.add(current_name)
        dfa_transitions[current_name] = {}

        for symbol in symbols:
            move_set = move(nfa, set(current), symbol)
            closure_set = nfa.epsilon_closure(move_set)

            if not closure_set:
                continue

            closure_frozen = frozenset(closure_set)
            if closure_frozen not in state_map:
                state_map[closure_frozen] = f"S{state_count}"
                unmarked.append(closure_frozen)
                state_count += 1

            dfa_transitions[current_name][symbol] = state_map[closure_frozen]

    for subset, name in state_map.items():
        if any(s in nfa.final_states for s in subset):
            dfa_final_states.add(name)

    dfa = DFA(
        states=dfa_states,
        alphabet=set(symbols),
        transition=dfa_transitions,
        start_state=state_map[frozenset(start_closure)],
        final_states=dfa_final_states,
    )
    return dfa.totalize()
