from dfa.dfa import DFA


def epsilon_closure(nfa, states):
    """Compute the ε-closure for a set of NFA states."""
    closure = set(states)
    stack = list(states)

    while stack:
        state = stack.pop()
        for next_state in nfa.transition.get(state, {}).get('ε', set()):
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
    return closure


def move(nfa, states, symbol):
    """Move from a set of states on a given symbol."""
    result = set()
    for state in states:
        result.update(nfa.transition.get(state, {}).get(symbol, set()))
    return result


def nfa_to_dfa(nfa):
    """Convert NFA (with optional ε-transitions) to DFA."""
    start_closure = epsilon_closure(nfa, {nfa.start_state})
    unmarked = [frozenset(start_closure)]
    dfa_states = set()
    dfa_transitions = {}
    dfa_final_states = set()
    state_map = {}  # frozenset → state name
    state_count = 0

    dead_state = "DEAD"
    dead_needed = False

    while unmarked:
        current = unmarked.pop()
        if current not in state_map:
            state_map[current] = f"S{state_count}"
            state_count += 1

        current_name = state_map[current]
        dfa_states.add(current_name)
        dfa_transitions[current_name] = {}

        for symbol in nfa.alphabet:
            if symbol == 'ε':
                continue  # DFA cannot have ε transitions

            move_set = move(nfa, current, symbol)
            closure_set = epsilon_closure(nfa, move_set)

            if not closure_set:
                dfa_transitions[current_name][symbol] = dead_state
                dead_needed = True
                continue

            closure_frozen = frozenset(closure_set)
            if closure_frozen not in state_map:
                state_map[closure_frozen] = f"S{state_count}"
                unmarked.append(closure_frozen)
                state_count += 1

            target_name = state_map[closure_frozen]
            dfa_transitions[current_name][symbol] = target_name

    # Final states: if any NFA final state is in the DFA subset
    for subset, name in state_map.items():
        if any(s in nfa.final_states for s in subset):
            dfa_final_states.add(name)

    if dead_needed:
        dfa_states.add(dead_state)
        dfa_transitions[dead_state] = {sym: dead_state for sym in nfa.alphabet if sym != 'ε'}

    return DFA(
        states=dfa_states,
        alphabet={s for s in nfa.alphabet if s != 'ε'},
        transition=dfa_transitions,
        start_state=state_map[frozenset(start_closure)],
        final_states=dfa_final_states
    )
