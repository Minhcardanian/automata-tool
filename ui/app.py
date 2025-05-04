import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, scrolledtext, Listbox
from PIL import Image, ImageTk
import json
import os
import sys

# Fix path for running from subdirectory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dfa.dfa import DFA
from dfa.from_nfa import nfa_to_dfa
from dfa.utils import print_dfa_table
from dfa.visualize import visualize_dfa
from nfa.nfa import NFA

class AutomataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automata Simulator")
        self.root.configure(bg="#f9f9f9")

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side="left", anchor="n", padx=10, pady=10)

        self.dfa = None
        self.input_string = ""
        self.current_index = 0
        self.current_state = None

        self.build_gui()

    def build_gui(self):
        self.file_frame = ttk.LabelFrame(self.left_frame, text="File Loader")
        self.file_frame.pack(fill="x")

        self.file_label = ttk.Label(self.file_frame, text="Select JSON file:")
        self.file_label.pack(side=ttk.LEFT, padx=5)

        self.file_list = Listbox(self.file_frame, height=5, width=30)
        self.file_list.pack(side=ttk.LEFT)
        self.populate_file_list()

        self.load_button = ttk.Button(self.file_frame, text="Load Selected File", bootstyle="primary", command=self.load_selected_file)
        self.load_button.pack(side=ttk.LEFT, padx=10)

        self.input_label = ttk.Label(self.left_frame, text="Enter input string:")
        self.input_label.pack()
        self.input_entry = ttk.Entry(self.left_frame, width=30)
        self.input_entry.pack()

        self.alphabet_label = ttk.Label(self.left_frame, text="", font=("Arial", 9))
        self.alphabet_label.pack(pady=2)

        self.test_button = ttk.Button(self.left_frame, text="Test Full String", bootstyle="primary", command=self.test_input)
        self.test_button.pack(pady=5)

        self.step_button = ttk.Button(self.left_frame, text="Step Through", bootstyle="primary", command=self.step_through)
        self.step_button.pack(pady=5)

        self.result_label = ttk.Label(self.left_frame, text="", font=("Arial", 14, "bold"))
        self.result_label.pack(pady=10)

        self.graph_button = ttk.Button(self.left_frame, text="Render DFA Graph", bootstyle="primary", command=self.render_graph)
        self.graph_button.pack(pady=5)

        self.image_label = ttk.Label(self.right_frame)
        self.image_label.pack(pady=5)

        ttk.Label(self.right_frame, text="Execution Log:", font=("Arial", 10, "bold")).pack()
        self.log_text = scrolledtext.ScrolledText(self.right_frame, height=8, width=80, bg="#ffffff")
        self.log_text.pack(pady=5)

        ttk.Label(self.right_frame, text="Transition Table:", font=("Arial", 10, "bold")).pack()
        self.table_text = scrolledtext.ScrolledText(self.right_frame, height=10, width=80, bg="#ffffff")
        self.table_text.pack(pady=5)

        self.clear_button = ttk.Button(self.right_frame, text="Clear All", bootstyle="danger", command=self.clear_all)
        self.clear_button.pack(pady=5)

    def populate_file_list(self):
        self.file_list.delete(0, ttk.END)
        for file in os.listdir("examples"):
            if file.endswith(".json"):
                self.file_list.insert(ttk.END, file)

    def load_selected_file(self):
        selection = self.file_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No file selected.")
            return

        filename = self.file_list.get(selection[0])
        path = os.path.join("examples", filename)
        try:
            with open(path, 'r') as f:
                data = json.load(f)

            transition = {
                state: {symbol: set(targets) for symbol, targets in trans.items()}
                for state, trans in data["transition"].items()
            }

            if any(symbol == 'ε' for trans in transition.values() for symbol in trans):
                nfa = NFA(
                    states=set(data["states"]),
                    alphabet=set(data["alphabet"]),
                    transition=transition,
                    start_state=data["start_state"],
                    final_states=set(data["final_states"])
                )
                self.dfa = nfa_to_dfa(nfa)
                messagebox.showinfo("Info", f"NFA loaded from '{filename}' and converted to DFA.")
            else:
                dfa_transition = {
                    state: {symbol: list(targets)[0] for symbol, targets in trans.items()}
                    for state, trans in transition.items()
                }
                self.dfa = DFA(
                    states=set(data["states"]),
                    alphabet=set(data["alphabet"]),
                    transition=dfa_transition,
                    start_state=data["start_state"],
                    final_states=set(data["final_states"])
                )
                messagebox.showinfo("Info", f"DFA loaded from '{filename}'.")

            self.current_index = 0
            self.input_string = ""
            self.current_state = self.dfa.start_state
            self.alphabet_label.config(text=f"Valid alphabet: {', '.join(self.dfa.alphabet)}")
            self.result_label.config(text="")
            self.log_text.delete('1.0', ttk.END)
            self.table_text.delete('1.0', ttk.END)
            self.capture_transition_table()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def capture_transition_table(self):
        import io
        buf = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buf
        print_dfa_table(self.dfa)
        sys.stdout = sys_stdout
        self.table_text.insert(ttk.END, buf.getvalue())

    def clear_all(self):
        self.input_entry.delete(0, ttk.END)
        self.result_label.config(text="")
        self.log_text.delete('1.0', ttk.END)
        self.table_text.delete('1.0', ttk.END)
        self.image_label.config(image='')
        self.alphabet_label.config(text="")

    def test_input(self):
        if not self.dfa:
            messagebox.showwarning("Warning", "Please load a DFA or NFA first.")
            return
        self.input_string = self.input_entry.get().strip()
        try:
            accepted = self.dfa.accepts(self.input_string)
            self.result_label.config(text="✅ Accepted" if accepted else "❌ Rejected", foreground="green" if accepted else "red")
        except Exception as e:
            self.result_label.config(text=f"Error: {e}", foreground="orange")

    def step_through(self):
        if not self.dfa:
            messagebox.showwarning("Warning", "Please load a DFA or NFA first.")
            return

        if self.current_index == 0:
            self.input_string = self.input_entry.get().strip()
            self.current_state = self.dfa.start_state
            self.log_text.delete('1.0', ttk.END)

        if self.current_index < len(self.input_string):
            symbol = self.input_string[self.current_index]
            try:
                next_state = self.dfa.transition[self.current_state][symbol]
                self.log_text.insert(ttk.END, f"Step {self.current_index + 1}: {self.current_state} --'{symbol}'--> {next_state}\n")
                self.current_state = next_state
                self.current_index += 1
            except KeyError:
                self.result_label.config(text=f"Error: Symbol '{symbol}' not valid from state '{self.current_state}'", foreground="orange")
                return
        else:
            accepted = self.current_state in self.dfa.final_states
            self.result_label.config(text="✅ Accepted" if accepted else "❌ Rejected", foreground="green" if accepted else "red")
            self.log_text.insert(ttk.END, f"[CURRENT STATE] {self.current_state}\n")
            self.current_index = 0

    def render_graph(self):
        if not self.dfa:
            messagebox.showwarning("Warning", "No DFA to render.")
            return

        visualize_dfa(self.dfa, view=False)
        try:
            img = Image.open("dfa_graph.png")
            max_width, max_height = 600, 400
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = AutomataApp(root)
    root.mainloop()
