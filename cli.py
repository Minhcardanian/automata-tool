from __future__ import annotations

import argparse

from automata_io import AutomatonFormatError, is_probably_nfa, load_automaton
from dfa.dfa import DFA
from dfa.from_nfa import nfa_to_dfa
from dfa.utils import print_dfa_table
from dfa.visualize import visualize_dfa
from nfa.nfa import NFA
from service import run_dfa


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automata simulator CLI")
    parser.add_argument("path", help="Path to automaton JSON")
    parser.add_argument(
        "--mode",
        choices=["auto", "dfa", "nfa"],
        default="auto",
        help="Input interpretation mode",
    )
    parser.add_argument("--visualize", action="store_true", help="Render DFA graph")
    parser.add_argument("--input", help="Single input to evaluate (non-interactive)")
    return parser


def _resolve_dfa(path: str, mode: str) -> DFA:
    automaton = load_automaton(path)

    if mode == "dfa":
        if isinstance(automaton, NFA):
            raise AutomatonFormatError("File describes an NFA but --mode dfa was requested.")
        return automaton

    if mode == "nfa":
        if isinstance(automaton, DFA):
            raise AutomatonFormatError("File describes a DFA but --mode nfa was requested.")
        return nfa_to_dfa(automaton)

    if isinstance(automaton, NFA):
        return nfa_to_dfa(automaton)
    return automaton


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.mode == "auto":
            probable_nfa = is_probably_nfa(args.path)
            print(f"[INFO] Auto-detected automaton type: {'NFA' if probable_nfa else 'DFA'}")

        dfa = _resolve_dfa(args.path, args.mode)
        print_dfa_table(dfa)

        if args.visualize:
            visualize_dfa(dfa, view=False)

        if args.input is not None:
            print("✅ Accepted" if dfa.accepts(args.input) else "❌ Rejected")
        else:
            run_dfa(dfa)

    except AutomatonFormatError as e:
        print(f"[ERROR] Invalid automaton format: {e}")
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
