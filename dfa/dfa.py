from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set


TransitionMap = Dict[str, Dict[str, str]]


@dataclass(slots=True)
class DFA:
    states: Set[str]
    alphabet: Set[str]
    transition: TransitionMap = field(default_factory=dict)
    start_state: str = ""
    final_states: Set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.states = set(self.states)
        self.alphabet = set(self.alphabet)
        self.final_states = set(self.final_states)
        self.transition = {
            state: dict(symbol_map)
            for state, symbol_map in self.transition.items()
        }

        if self.start_state not in self.states:
            raise ValueError(f"Start state '{self.start_state}' is not in states.")

        missing_finals = self.final_states - self.states
        if missing_finals:
            raise ValueError(
                f"Final states not in states: {sorted(missing_finals)}"
            )

        for src, symbol_map in self.transition.items():
            if src not in self.states:
                raise ValueError(f"Transition source state '{src}' is not in states.")
            for symbol, dst in symbol_map.items():
                if symbol not in self.alphabet:
                    raise ValueError(
                        f"Transition symbol '{symbol}' from '{src}' is not in alphabet."
                    )
                if dst not in self.states:
                    raise ValueError(
                        f"Transition target state '{dst}' from '{src}' is not in states."
                    )

    def is_total(self) -> bool:
        return all(
            symbol in self.transition.get(state, {})
            for state in self.states
            for symbol in self.alphabet
        )

    def totalize(self, dead_state: str = "DEAD") -> "DFA":
        if self.is_total():
            return self

        states = set(self.states)
        transition = {state: dict(self.transition.get(state, {})) for state in states}

        while dead_state in states:
            dead_state = f"{dead_state}_1"

        states.add(dead_state)
        transition[dead_state] = {symbol: dead_state for symbol in self.alphabet}

        for state in states:
            if state not in transition:
                transition[state] = {}
            for symbol in self.alphabet:
                transition[state].setdefault(symbol, dead_state)

        return DFA(
            states=states,
            alphabet=set(self.alphabet),
            transition=transition,
            start_state=self.start_state,
            final_states=set(self.final_states),
        )

    def accepts(self, input_string: str) -> bool:
        current_state = self.start_state
        for symbol in input_string:
            if symbol not in self.alphabet:
                raise ValueError(f"Symbol '{symbol}' not in DFA alphabet.")
            if symbol not in self.transition.get(current_state, {}):
                return False
            current_state = self.transition[current_state][symbol]
        return current_state in self.final_states
