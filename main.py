from __future__ import annotations

from automata_io import is_probably_nfa, load_automaton
from cli import main as cli_main
from dfa.dfa import DFA
from nfa.nfa import NFA


def load_dfa_from_json(path: str) -> DFA:
    automaton = load_automaton(path)
    if isinstance(automaton, NFA):
        raise TypeError("Expected DFA JSON, but detected NFA structure.")
    return automaton


def load_nfa_from_json(path: str) -> NFA:
    automaton = load_automaton(path)
    if isinstance(automaton, DFA):
        raise TypeError("Expected NFA JSON, but detected DFA structure.")
    return automaton


if __name__ == "__main__":
    cli_main()
