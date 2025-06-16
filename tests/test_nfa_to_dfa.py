import json
import sys
import random
from itertools import product
from pathlib import Path

import pytest

# Ensure repository root is on the path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from dfa.from_nfa import nfa_to_dfa
from nfa.nfa import NFA

EXAMPLES_DIR = ROOT_DIR / "examples"
NFA_EXAMPLES = sorted(EXAMPLES_DIR.glob("*nfa*.json"))


def load_nfa(path: str) -> NFA:
    with open(path) as f:
        data = json.load(f)
    transition = {
        s: {sym: set(tgt) for sym, tgt in trans.items()}
        for s, trans in data["transition"].items()
    }
    return NFA(
        states=set(data["states"]),
        alphabet=set(data["alphabet"]),
        transition=transition,
        start_state=data["start_state"],
        final_states=set(data["final_states"]),
    )


def generate_strings(alphabet, max_length=3):
    yield ""
    for length in range(1, max_length + 1):
        for prod in product(alphabet, repeat=length):
            yield "".join(prod)


@pytest.mark.parametrize("path", [str(p) for p in NFA_EXAMPLES])
def test_nfa_conversion_matches_dfa(path, capsys):
    """
    Standard JSON examples: NFA vs. DFA acceptance for all strings up to length 3.
    """
    nfa = load_nfa(path)
    dfa = nfa_to_dfa(nfa)
    alphabet = [sym for sym in nfa.alphabet if sym != "ε"]
    for s in generate_strings(alphabet):
        assert nfa.accepts(s) == dfa.accepts(s), f"{path}: mismatch for '{s}'"
    with capsys.disabled():
        print(f"Verified {Path(path).name}")


def test_epsilon_chain_and_loop_edge_case(capsys):
    nfa = NFA(
        states={'A','B','C','D'},
        alphabet={'0','1'},
        transition={
            'A': {'ε': {'B'}},
            'B': {'ε': {'C'}},
            'C': {'ε': {'B','D'}, '0': {'D'}},
            'D': {'1': {'D'}}
        },
        start_state='A',
        final_states={'D'}
    )
    dfa = nfa_to_dfa(nfa)
    for s in ['', '0', '1', '00', '11', '01', '10', '101']:
        assert nfa.accepts(s) == dfa.accepts(s), f"epsilon-chain mismatch for '{s}'"


def test_nfa_with_dead_state(capsys):
    nfa = NFA(
        states={'q0','q1'},
        alphabet={'a','b'},
        transition={
            'q0': {'a': {'q1'}},
            'q1': {'a': {'q1'}},
        },
        start_state='q0',
        final_states={'q1'}
    )
    dfa = nfa_to_dfa(nfa)
    # Empty string should be rejected since start_state is non-final
    assert not dfa.accepts(''), "dead-state should reject empty string"
    # Strings of only 'a's should be accepted
    for s in ['a', 'aa', 'aaa']:
        assert dfa.accepts(s), f"dead-state should accept '{s}'"
    # Strings containing 'b' or starting with b should be rejected
    for s in ['b', 'ab', 'ba', 'bb']:
        assert not dfa.accepts(s), f"dead-state should reject '{s}'"


def test_unreachable_states():
    # NFA with an unreachable state 'X'
    nfa = NFA(
        states={'S','F','X'},
        alphabet={'0'},
        transition={'S': {'0': {'F'}}},
        start_state='S',
        final_states={'F'}
    )
    dfa = nfa_to_dfa(nfa)
    assert dfa.accepts('0')
    assert not dfa.accepts('')


def test_epsilon_only_acceptance():
    # Start state is final, acceptance via epsilon only
    nfa = NFA(
        states={'S','A'},
        alphabet={'a'},
        transition={'S': {'ε': {'A'}}},
        start_state='S',
        final_states={'S','A'}
    )
    dfa = nfa_to_dfa(nfa)
    assert dfa.accepts('')
    assert not dfa.accepts('a')


def test_branching_nondeterminism():
    # One state branches to many on same symbol
    targets = {f'Q{i}' for i in range(5)}
    nfa = NFA(
        states={'S'} | targets,
        alphabet={'x'},
        transition={'S': {'x': targets}},
        start_state='S',
        final_states={next(iter(targets))}
    )
    dfa = nfa_to_dfa(nfa)
    assert dfa.accepts('x')
    assert not dfa.accepts('xx')


def test_larger_alphabet_and_longer_strings():
    # Alphabet of size 3, strings up to length 4
    states = {'S','A','B'}
    alphabet = {'0','1','2'}
    transition = {
        'S': {'0':{'A'}, '1':{'B'}, '2':{'A'}},
        'A': {'0':{'B'}, '1':{'A'}, '2':{'B'}},
        'B': {'0':{'S'}, '1':{'S'}, '2':{'S'}},
    }
    nfa = NFA(states, alphabet, transition, 'S', {'S'})
    dfa = nfa_to_dfa(nfa)
    for s in generate_strings(alphabet, max_length=4):
        assert nfa.accepts(s) == dfa.accepts(s), f"larger alpha mismatch for '{s}'"


def test_random_nfa_fuzz():
    # Generate small random NFAs with seed
    random.seed(42)
    for _ in range(5):
        num_states = 3
        states = [f"q{i}" for i in range(num_states)]
        alphabet = {'0','1'}
        transition = {}
        for s in states:
            transition[s] = {}
            for sym in alphabet | {'ε'}:
                # randomly choose subset of states
                k = random.randint(0, num_states)
                transition[s][sym] = set(random.sample(states, k))
        start = states[0]
        finals = set(random.sample(states, random.randint(1, num_states)))
        nfa = NFA(set(states), alphabet, transition, start, finals)
        dfa = nfa_to_dfa(nfa)
        for s in generate_strings(alphabet):
            assert nfa.accepts(s) == dfa.accepts(s), f"random NFA mismatch for '{s}'"


if __name__ == "__main__":
    # Print and run
    print("Found NFA example files:")
    for p in NFA_EXAMPLES:
        print(f"  • {p.name}")
    print("\nRunning tests…")
    import pytest as _pytest
    exit_code = _pytest.main([__file__, "-q"])
    if exit_code == 0:
        print("\nAll tests passed ")
    sys.exit(exit_code)
