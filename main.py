import json
from dfa.dfa import DFA
from nfa.nfa import NFA
from dfa.from_nfa import nfa_to_dfa
from dfa.visualize import visualize_dfa
from dfa.utils import print_dfa_table

def load_dfa_from_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return DFA(
        states=set(data["states"]),
        alphabet=set(data["alphabet"]),
        transition=data["transition"],
        start_state=data["start_state"],
        final_states=set(data["final_states"])
    )

def load_nfa_from_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    # Convert nested lists to sets for transitions
    transition = {
        state: {symbol: set(targets) for symbol, targets in trans.items()}
        for state, trans in data["transition"].items()
    }
    return NFA(
        states=set(data["states"]),
        alphabet=set(data["alphabet"]),
        transition=transition,
        start_state=data["start_state"],
        final_states=set(data["final_states"])
    )

def is_probably_nfa(path):
    with open(path, "r") as f:
        data = json.load(f)
    return any(
        symbol == 'ε' or isinstance(targets, list)
        for trans in data["transition"].values()
        for symbol, targets in trans.items()
    )

def run_dfa(dfa):
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

if __name__ == "__main__":
    while True:
        print("Choose mode:")
        print("1. Run DFA")
        print("2. Run NFA → DFA")
        mode = input("Enter 1 or 2 (or 'exit' to quit): ").strip()

        if mode == "exit":
            break

        if mode == "1":
            filename = input("Enter DFA JSON filename (in examples/): ").strip()
            path = f"examples/{filename}"
            try:
                if is_probably_nfa(path):
                    print("[WARNING] This file looks like an NFA. You may want to use mode 2.")
                    proceed = input("Do you want to continue anyway? (y/n): ").strip().lower()
                    if proceed != 'y':
                        continue
                dfa = load_dfa_from_json(path)
                print(f"[INFO] DFA loaded from '{filename}'.")
                print_dfa_table(dfa)
                run_dfa(dfa)
            except Exception as e:
                print(f"[ERROR] Failed to load DFA: {e}")

        elif mode == "2":
            filename = input("Enter NFA JSON filename (in examples/): ").strip()
            path = f"examples/{filename}"
            try:
                if not is_probably_nfa(path):
                    print("[WARNING] This file may be a DFA. You may want to use mode 1.")
                    proceed = input("Do you want to continue anyway? (y/n): ").strip().lower()
                    if proceed != 'y':
                        continue
                nfa = load_nfa_from_json(path)
                print(f"[INFO] NFA loaded from '{filename}'.")
                dfa = nfa_to_dfa(nfa)
                print("[INFO] NFA converted to DFA.")
                print_dfa_table(dfa)
                visualize_dfa(dfa, view=False)
                run_dfa(dfa)
            except Exception as e:
                print(f"[ERROR] Failed to load or convert NFA: {e}")

        else:
            print("Invalid mode.")
