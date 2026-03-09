import json
import random
import sys
from itertools import product
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from automata_io import AutomatonFormatError, TransitionValidationError, load_automaton
from dfa.from_nfa import epsilon_closure, nfa_to_dfa
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
    alphabet = sorted(sym for sym in nfa.alphabet if sym != "ε")
    for s in generate_strings(alphabet):
        assert nfa.accepts(s) == dfa.accepts(s), f"{path}: mismatch for '{s}'"
    with capsys.disabled():
        print(f"Verified {Path(path).name}")


def test_backward_compatible_module_epsilon_closure():
    nfa = NFA(
        states={"A", "B", "C"},
        alphabet={"0"},
        transition={"A": {"ε": {"B"}}, "B": {"ε": {"C"}}, "C": {}},
        start_state="A",
        final_states={"C"},
    )
    assert epsilon_closure(nfa, {"A"}) == {"A", "B", "C"}


def test_epsilon_chain_and_loop_edge_case():
    nfa = NFA(
        states={"A", "B", "C", "D"},
        alphabet={"0", "1"},
        transition={
            "A": {"ε": {"B"}},
            "B": {"ε": {"C"}},
            "C": {"ε": {"B", "D"}, "0": {"D"}},
            "D": {"1": {"D"}},
        },
        start_state="A",
        final_states={"D"},
    )
    dfa = nfa_to_dfa(nfa)
    for s in ["", "0", "1", "00", "11", "01", "10", "101"]:
        assert nfa.accepts(s) == dfa.accepts(s), f"epsilon-chain mismatch for '{s}'"


def test_nfa_with_dead_state():
    nfa = NFA(
        states={"q0", "q1"},
        alphabet={"a", "b"},
        transition={"q0": {"a": {"q1"}}, "q1": {"a": {"q1"}}},
        start_state="q0",
        final_states={"q1"},
    )
    dfa = nfa_to_dfa(nfa)
    assert dfa.is_total()
    assert not dfa.accepts("")
    for s in ["a", "aa", "aaa"]:
        assert dfa.accepts(s)
    for s in ["b", "ab", "ba", "bb"]:
        assert not dfa.accepts(s)


def test_unreachable_states():
    nfa = NFA(
        states={"S", "F", "X"},
        alphabet={"0"},
        transition={"S": {"0": {"F"}}},
        start_state="S",
        final_states={"F"},
    )
    dfa = nfa_to_dfa(nfa)
    assert dfa.accepts("0")
    assert not dfa.accepts("")


def test_epsilon_only_acceptance():
    nfa = NFA(
        states={"S", "A"},
        alphabet={"a"},
        transition={"S": {"ε": {"A"}}},
        start_state="S",
        final_states={"S", "A"},
    )
    dfa = nfa_to_dfa(nfa)
    assert dfa.accepts("")
    assert not dfa.accepts("a")


def test_branching_nondeterminism():
    targets = {f"Q{i}" for i in range(5)}
    nfa = NFA(
        states={"S"} | targets,
        alphabet={"x"},
        transition={"S": {"x": targets}},
        start_state="S",
        final_states={next(iter(targets))},
    )
    dfa = nfa_to_dfa(nfa)
    assert dfa.accepts("x")
    assert not dfa.accepts("xx")


def test_larger_alphabet_and_longer_strings():
    states = {"S", "A", "B"}
    alphabet = {"0", "1", "2"}
    transition = {
        "S": {"0": {"A"}, "1": {"B"}, "2": {"A"}},
        "A": {"0": {"B"}, "1": {"A"}, "2": {"B"}},
        "B": {"0": {"S"}, "1": {"S"}, "2": {"S"}},
    }
    nfa = NFA(states, alphabet, transition, "S", {"S"})
    dfa = nfa_to_dfa(nfa)
    for s in generate_strings(alphabet, max_length=4):
        assert nfa.accepts(s) == dfa.accepts(s), f"larger alpha mismatch for '{s}'"


def test_validation_error_for_unknown_transition_target(tmp_path):
    bad = {
        "states": ["q0"],
        "alphabet": ["a"],
        "transition": {"q0": {"a": ["qX"]}},
        "start_state": "q0",
        "final_states": ["q0"],
    }
    file = tmp_path / "bad_target.json"
    file.write_text(json.dumps(bad), encoding="utf-8")

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
    file.write_text(json.dumps(bad), encoding="utf-8")

    with pytest.raises(AutomatonFormatError):
        load_automaton(file)


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
