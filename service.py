from __future__ import annotations

from pathlib import Path

from automata_io import load_automaton
from dfa.dfa import DFA
from dfa.from_nfa import nfa_to_dfa
from nfa.nfa import NFA


def load_dfa(path: str | Path) -> DFA:
    automaton = load_automaton(path)
    if isinstance(automaton, NFA):
        raise TypeError("Loaded automaton is NFA; expected DFA.")
    return automaton


def load_as_dfa(path: str | Path) -> DFA:
    automaton = load_automaton(path)
    if isinstance(automaton, NFA):
        return nfa_to_dfa(automaton)
    return automaton


def run_dfa(dfa: DFA) -> None:
    print("Enter strings to test. Type 'exit' to quit.")
    while True:
        s = input("Input string: ").strip()
        if s.lower() == "exit":
            break
        try:
            result = dfa.accepts(s)
            print("✅ Accepted" if result else "❌ Rejected")
        except ValueError as e:
            print(f"Error: {e}")
