from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Set


EPSILON = "ε"
TransitionMap = Dict[str, Dict[str, Set[str]]]


@dataclass(slots=True)
class NFA:
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
            state: {
                symbol: set(targets)
                for symbol, targets in symbol_map.items()
            }
            for state, symbol_map in self.transition.items()
        }

        self.alphabet.discard(EPSILON)

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
            for symbol, targets in symbol_map.items():
                if symbol != EPSILON and symbol not in self.alphabet:
                    raise ValueError(
                        f"Transition symbol '{symbol}' from '{src}' is not in alphabet."
                    )
                unknown_targets = set(targets) - self.states
                if unknown_targets:
                    raise ValueError(
                        f"Transition from '{src}' has unknown target states: "
                        f"{sorted(unknown_targets)}"
                    )

    def move(self, state_set: Iterable[str], symbol: str) -> Set[str]:
        result: Set[str] = set()
        for state in state_set:
            result.update(self.transition.get(state, {}).get(symbol, set()))
        return result

    def epsilon_closure(self, state_set: Iterable[str]) -> Set[str]:
        stack = list(state_set)
        closure = set(state_set)
        while stack:
            state = stack.pop()
            for next_state in self.transition.get(state, {}).get(EPSILON, set()):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def lambda_closure(self, state_set: Iterable[str]) -> Set[str]:
        return self.epsilon_closure(state_set)

    def accepts(self, input_string: str) -> bool:
        current_states = self.epsilon_closure({self.start_state})
        for symbol in input_string:
            if symbol not in self.alphabet:
                raise ValueError(f"Symbol '{symbol}' not in NFA alphabet.")
            next_states = self.move(current_states, symbol)
            current_states = self.epsilon_closure(next_states)
        return any(s in self.final_states for s in current_states)
