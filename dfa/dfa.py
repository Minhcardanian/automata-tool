class DFA:
    def __init__(self, states, alphabet, transition, start_state, final_states):
        self.states = states                          # Set of states
        self.alphabet = alphabet                      # Input alphabet
        self.transition = transition                  # Dict[state][symbol] = next_state
        self.start_state = start_state
        self.final_states = final_states

    def accepts(self, input_string):
        current_state = self.start_state
        for symbol in input_string:
            if symbol not in self.alphabet:
                raise ValueError(f"Symbol '{symbol}' not in DFA alphabet.")
            if current_state not in self.transition or symbol not in self.transition[current_state]:
                return False
            current_state = self.transition[current_state][symbol]
        return current_state in self.final_states
