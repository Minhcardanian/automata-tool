class NFA:
    def __init__(self, states, alphabet, transition, start_state, final_states):
        self.states = states                            # Set of states
        self.alphabet = alphabet                        # Set of input symbols (exclude 'ε')
        self.transition = transition                    # Dict[state][symbol] = set of next states
        self.start_state = start_state
        self.final_states = final_states

    def move(self, state_set, symbol):
        """Move from a set of states on a symbol"""
        result = set()
        for state in state_set:
            if state in self.transition and symbol in self.transition[state]:
                result.update(self.transition[state][symbol])
        return result

    def lambda_closure(self, state_set):
        """Compute λ-closure (ε-closure) of a set of states"""
        stack = list(state_set)
        closure = set(state_set)
        while stack:
            state = stack.pop()
            if state in self.transition and 'ε' in self.transition[state]:
                for next_state in self.transition[state]['ε']:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        return closure

    def accepts(self, input_string):
        """Return True if the NFA accepts the given string."""
        current_states = self.lambda_closure({self.start_state})
        for symbol in input_string:
            if symbol not in self.alphabet:
                raise ValueError(f"Symbol '{symbol}' not in NFA alphabet.")
            next_states = self.move(current_states, symbol)
            current_states = self.lambda_closure(next_states)
        return any(s in self.final_states for s in current_states)
