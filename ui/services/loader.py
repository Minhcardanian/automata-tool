from __future__ import annotations

from pathlib import Path

from dfa.dfa import DFA
from dfa.from_nfa import nfa_to_dfa
from nfa.nfa import NFA
from automata_io import load_automaton


def list_json_examples(examples_dir: str | Path) -> list[str]:
    return sorted(
        path.name
        for path in Path(examples_dir).iterdir()
        if path.suffix == ".json"
    )


def load_as_dfa(path: str | Path) -> tuple[DFA, str]:
    automaton = load_automaton(path)
    if isinstance(automaton, NFA):
        return nfa_to_dfa(automaton), "NFA → DFA"
    return automaton, "DFA"
