def print_dfa_table(dfa):
    states = sorted(dfa.states)
    alphabet = sorted(dfa.alphabet)

    # Define column widths
    col_width = max(max(len(s) for s in states), 6)
    sym_width = max(max(len(sym) for sym in alphabet), 3)
    cell_width = max(col_width, sym_width) + 2

    def pad(s): return str(s).ljust(cell_width)

    # Print header
    print("\nDFA Transition Table:")
    header = [pad("State")] + [pad(sym) for sym in alphabet]
    print("".join(header))
    print("-" * (cell_width * (len(alphabet) + 1)))

    # Print each row
    for state in states:
        row = [pad(state)]
        for symbol in alphabet:
            target = dfa.transition.get(state, {}).get(symbol, "-")
            row.append(pad(target))
        print("".join(row))

    # Start & Final
    print(f"\nStart State : {dfa.start_state}")
    print(f"Final States: {dfa.final_states}\n")
