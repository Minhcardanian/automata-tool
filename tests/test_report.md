# NFA → DFA Conversion Test Report

This report summarizes the suite of tests implemented in `tests/test_nfa_to_dfa.py` to verify the correctness of the NFA simulation logic and the subset-construction algorithm (`nfa_to_dfa`).

## Test Categories and Coverage

1. **Standard JSON Examples** (`test_nfa_conversion_matches_dfa`)

   * Loads each NFA example from `examples/*nfa*.json`.
   * Converts to DFA and compares acceptance for all strings over the NFA's alphabet up to length 3.
   * Verifies that the DFA matches the NFA's behavior on each example file.

2. **Edge-Case Tests**

   * **Epsilon-Closure Chains and Loops** (`test_epsilon_chain_and_loop_edge_case`)

     * NFA with multi-level ε-transitions and cycles.
     * Ensures λ-closure handles arbitrary chaining and loops correctly.
   * **Dead-State Handling** (`test_nfa_with_dead_state`)

     * NFA with missing transitions (dead paths) and non-final start state.
     * Confirms empty-string rejection, correct acceptance of valid strings, and rejection of invalid symbols.
   * **Unreachable States** (`test_unreachable_states`)

     * NFA containing a state never reachable from the start.
     * Ensures unreachable states do not affect acceptance.
   * **Epsilon-Only Acceptance** (`test_epsilon_only_acceptance`)

     * NFA where acceptance depends solely on ε-moves (start state is final via ε).
     * Verifies empty-string acceptance and rejection of non-empty input.
   * **Branching Nondeterminism** (`test_branching_nondeterminism`)

     * Single-state NFA branching to multiple targets on the same symbol.
     * Checks correct DFA state-merge and acceptance for single-step inputs.

3. **Stress and Combinatorial Tests**

   * **Larger Alphabet & Longer Strings** (`test_larger_alphabet_and_longer_strings`)

     * Alphabet size of 3, string lengths up to 4.
     * Confirms exponential growth in subset construction remains correct.
   * **Random NFA Fuzz Testing** (`test_random_nfa_fuzz`)

     * Generates 5 small random NFAs (3 states + ε) with a fixed seed.
     * Compares NFA and DFA acceptance for all strings up to length 3.
     * Catches high-probability corner cases through randomized structure.

## Execution Summary

* **Total test cases:** 14 (7 JSON examples + 7 custom/fuzz tests)
* **Test runner:** pytest
* **Invocation:** `python tests/test_nfa_to_dfa.py` or `pytest -q`
* **Result:** All tests pass, confirming:

  * Correct computation of λ-closures and moves
  * Accurate subset-construction and dead-state propagation
  * Proper handling of unreachable and branching scenarios
  * Robustness under randomized NFA topologies


