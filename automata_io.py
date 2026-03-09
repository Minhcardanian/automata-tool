from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dfa.dfa import DFA
from nfa.nfa import EPSILON, NFA


class AutomatonFormatError(ValueError):
    pass


class TransitionValidationError(AutomatonFormatError):
    pass


def _expect_keys(data: dict[str, Any], required: set[str]) -> None:
    missing = required - data.keys()
    if missing:
        raise AutomatonFormatError(f"Missing keys: {sorted(missing)}")


def _as_state_set(value: Any, key: str) -> set[str]:
    if not isinstance(value, list) or not all(isinstance(s, str) for s in value):
        raise AutomatonFormatError(f"'{key}' must be a list of strings.")
    return set(value)


def _validate_common(data: dict[str, Any]) -> tuple[set[str], set[str], str, set[str], dict[str, Any]]:
    _expect_keys(data, {"states", "alphabet", "transition", "start_state", "final_states"})

    states = _as_state_set(data["states"], "states")
    alphabet = _as_state_set(data["alphabet"], "alphabet")
    final_states = _as_state_set(data["final_states"], "final_states")
    start_state = data["start_state"]

    if not isinstance(start_state, str):
        raise AutomatonFormatError("'start_state' must be a string.")
    if start_state not in states:
        raise AutomatonFormatError(f"start_state '{start_state}' is not listed in states.")

    unknown_finals = final_states - states
    if unknown_finals:
        raise AutomatonFormatError(f"final_states contain unknown states: {sorted(unknown_finals)}")

    transition = data["transition"]
    if not isinstance(transition, dict):
        raise AutomatonFormatError("'transition' must be an object.")

    return states, alphabet, start_state, final_states, transition


def _detect_nfa(transition: dict[str, Any]) -> bool:
    for state_map in transition.values():
        if not isinstance(state_map, dict):
            continue
        for symbol, targets in state_map.items():
            if symbol == EPSILON or isinstance(targets, list):
                return True
    return False


def _parse_nfa_transition(states: set[str], alphabet: set[str], transition: dict[str, Any]) -> dict[str, dict[str, set[str]]]:
    parsed: dict[str, dict[str, set[str]]] = {}
    for src, symbol_map in transition.items():
        if src not in states:
            raise TransitionValidationError(f"Transition source '{src}' is not in states.")
        if not isinstance(symbol_map, dict):
            raise TransitionValidationError(f"Transition map for '{src}' must be an object.")

        parsed[src] = {}
        for symbol, raw_targets in symbol_map.items():
            if symbol != EPSILON and symbol not in alphabet:
                raise TransitionValidationError(
                    f"Transition symbol '{symbol}' from '{src}' is not in alphabet."
                )

            if isinstance(raw_targets, list):
                targets = set(raw_targets)
            elif isinstance(raw_targets, str):
                targets = {raw_targets}
            else:
                raise TransitionValidationError(
                    f"Targets for '{src}' on '{symbol}' must be a string or list of strings."
                )

            if not all(isinstance(t, str) for t in targets):
                raise TransitionValidationError(
                    f"Targets for '{src}' on '{symbol}' must be strings."
                )

            unknown_targets = targets - states
            if unknown_targets:
                raise TransitionValidationError(
                    f"Transition '{src}' --{symbol}--> has unknown targets: {sorted(unknown_targets)}"
                )
            parsed[src][symbol] = targets
    return parsed


def _parse_dfa_transition(states: set[str], alphabet: set[str], transition: dict[str, Any]) -> dict[str, dict[str, str]]:
    parsed: dict[str, dict[str, str]] = {}
    for src, symbol_map in transition.items():
        if src not in states:
            raise TransitionValidationError(f"Transition source '{src}' is not in states.")
        if not isinstance(symbol_map, dict):
            raise TransitionValidationError(f"Transition map for '{src}' must be an object.")

        parsed[src] = {}
        for symbol, raw_target in symbol_map.items():
            if symbol not in alphabet:
                raise TransitionValidationError(
                    f"Transition symbol '{symbol}' from '{src}' is not in alphabet."
                )
            if isinstance(raw_target, list):
                if len(raw_target) != 1 or not isinstance(raw_target[0], str):
                    raise TransitionValidationError(
                        f"DFA transition '{src}' --{symbol}--> must have a single target state."
                    )
                target = raw_target[0]
            elif isinstance(raw_target, str):
                target = raw_target
            else:
                raise TransitionValidationError(
                    f"Target for '{src}' on '{symbol}' must be a string."
                )
            if target not in states:
                raise TransitionValidationError(
                    f"Transition target '{target}' from '{src}' is not in states."
                )
            parsed[src][symbol] = target
    return parsed


def load_automaton(path: str | Path) -> DFA | NFA:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise AutomatonFormatError("JSON root must be an object.")

    states, alphabet, start_state, final_states, transition = _validate_common(data)
    is_nfa = _detect_nfa(transition)

    if is_nfa:
        parsed_transition = _parse_nfa_transition(states, alphabet, transition)
        return NFA(states, alphabet, parsed_transition, start_state, final_states)

    parsed_transition = _parse_dfa_transition(states, alphabet, transition)
    return DFA(states, alphabet, parsed_transition, start_state, final_states)


def is_probably_nfa(path: str | Path) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    transition = data.get("transition", {}) if isinstance(data, dict) else {}
    return _detect_nfa(transition)
