import random
import sys
from itertools import product
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from automata_io import AutomatonFormatError, TransitionValidationError, load_automaton
from dfa.from_nfa import nfa_to_dfa
from nfa.nfa import NFA

EXAMPLES_DIR = ROOT_DIR / "examples"
NFA_EXAMPLES = sorted(EXAMPLES_DIR.glob("*nfa*.json"))


def load_nfa(path: str) -> NFA:
    automaton = load_automaton(path)
    assert isinstance(automaton, NFA)
    return automaton


def generate_strings(alphabet, max_length=3):
    yield ""
    for length in range(1, max_length + 1):
        for prod in product(alphabet, repeat=length):
            yield "".join(prod)


@pytest.mark.parametrize("path", [str(p) for p in NFA_EXAMPLES])
def test_nfa_conversion_matches_dfa(path, capsys):
    nfa = load_nfa(path)
    dfa = nfa_to_dfa(nfa)
    alphabet = sorted(nfa.alphabet)
    for s in generate_strings(alphabet):
        assert nfa.accepts(s) == dfa.accepts(s), f"{path}: mismatch for '{s}'"
    with capsys.disabled():
        print(f"Verified {Path(path).name}")


def test_validation_error_for_unknown_transition_target(tmp_path):
    bad = {
        "states": ["q0"],
        "alphabet": ["a"],
        "transition": {"q0": {"a": ["qX"]}},
        "start_state": "q0",
        "final_states": ["q0"],
    }
    file = tmp_path / "bad_target.json"
    file.write_text(__import__("json").dumps(bad), encoding="utf-8")

    with pytest.raises(TransitionValidationError):
        load_automaton(file)


def test_validation_error_for_missing_required_key(tmp_path):
    bad = {
        "states": ["q0"],
        "alphabet": ["a"],
        "start_state": "q0",
        "final_states": ["q0"],
    }
    file = tmp_path / "missing_key.json"
    file.write_text(__import__("json").dumps(bad), encoding="utf-8")

    with pytest.raises(AutomatonFormatError):
        load_automaton(file)


def test_dfa_is_total_after_conversion():
    nfa = NFA(
        states={"q0", "q1"},
        alphabet={"a", "b"},
        transition={"q0": {"a": {"q1"}}, "q1": {"a": {"q1"}}},
        start_state="q0",
        final_states={"q1"},
    )
    dfa = nfa_to_dfa(nfa)
    assert dfa.is_total()


@pytest.mark.slow
def test_random_nfa_fuzz():
    random.seed(42)
    for _ in range(5):
        num_states = 3
        states = [f"q{i}" for i in range(num_states)]
        alphabet = {"0", "1"}
        transition = {}
        for s in states:
            transition[s] = {}
            for sym in alphabet | {"ε"}:
                k = random.randint(0, num_states)
                transition[s][sym] = set(random.sample(states, k))
        start = states[0]
        finals = set(random.sample(states, random.randint(1, num_states)))
        nfa = NFA(set(states), alphabet, transition, start, finals)
        dfa = nfa_to_dfa(nfa)
        for s in generate_strings(alphabet):
            assert nfa.accepts(s) == dfa.accepts(s), f"random NFA mismatch for '{s}'"
