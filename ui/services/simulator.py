from __future__ import annotations

from dfa.dfa import DFA


def validate_input_symbols(dfa: DFA, input_string: str) -> str | None:
    for ch in input_string:
        if ch not in dfa.alphabet:
            return ch
    return None


def step_transition(dfa: DFA, state: str, symbol: str) -> str | None:
    return dfa.transition.get(state, {}).get(symbol)
