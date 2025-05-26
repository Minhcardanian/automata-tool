import tkinter as tk
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

        # Main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Left and right panels
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side="left", anchor="n", padx=10, pady=10)

        # Automaton state
        self.dfa = None
        self.input_string = ""
        self.current_index = 0
        self.current_state = None
        self.highlight_edges = None
        self.highlight_nodes = None

        self.build_gui()

    def build_gui(self):
        # File loader
        self.file_frame = ttk.LabelFrame(self.left_frame, text="File Loader")
        self.file_frame.pack(fill="x")
        ttk.Label(self.file_frame, text="Select JSON file:").pack(side=ttk.LEFT, padx=5)
        self.file_list = Listbox(self.file_frame, height=5, width=30)
        self.file_list.pack(side=ttk.LEFT)
        self.populate_file_list()
        ttk.Button(self.file_frame, text="Load Selected File", bootstyle="primary",
                   command=self.load_selected_file).pack(side=ttk.LEFT, padx=10)

        # Input controls
        ttk.Label(self.left_frame, text="Enter input string:").pack(pady=(10,0))
        self.input_entry = ttk.Entry(self.left_frame, width=30)
        self.input_entry.pack()
        self.alphabet_label = ttk.Label(self.left_frame, text="", font=("Arial", 9))
        self.alphabet_label.pack(pady=2)

        ttk.Button(self.left_frame, text="Test Full String", bootstyle="primary",
                   command=self.test_input).pack(pady=5)
        ttk.Button(self.left_frame, text="Step Through", bootstyle="primary",
                   command=self.step_through).pack(pady=5)

        self.result_label = ttk.Label(self.left_frame, text="", font=("Arial", 14, "bold"))
        self.result_label.pack(pady=10)
        ttk.Button(self.left_frame, text="Render DFA Graph", bootstyle="primary",
                   command=self.render_graph).pack(pady=5)

        # Visualization / logs / table
        self.image_label = ttk.Label(self.right_frame)
        self.image_label.pack(pady=5)

        ttk.Label(self.right_frame, text="Execution Log:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(self.right_frame, height=8, width=80, bg="#ffffff")
        self.log_text.pack(pady=5)

        ttk.Label(self.right_frame, text="Transition Table:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.table_text = scrolledtext.ScrolledText(self.right_frame, height=10, width=80, bg="#ffffff")
        self.table_text.pack(pady=5)

        ttk.Button(self.right_frame, text="Clear All", bootstyle="danger",
                   command=self.clear_all).pack(pady=5)

    def populate_file_list(self):
        self.file_list.delete(0, ttk.END)
        for fname in os.listdir("examples"):
            if fname.endswith(".json"):
                self.file_list.insert(ttk.END, fname)

    def load_selected_file(self):
        sel = self.file_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "No file selected.")
            return

        filename = self.file_list.get(sel[0])
        path = os.path.join("examples", filename)
        try:
            with open(path) as f:
                data = json.load(f)
            # build transition dict
            trans = {
                st: {sym: set(tgt) for sym, tgt in tr.items()}
                for st, tr in data["transition"].items()
            }
            # detect NFA vs DFA
            if any('ε' == sym for tr in trans.values() for sym in tr):
                nfa = NFA(
                    states=set(data["states"]),
                    alphabet=set(data["alphabet"]),
                    transition=trans,
                    start_state=data["start_state"],
                    final_states=set(data["final_states"])
                )
                self.dfa = nfa_to_dfa(nfa)
                messagebox.showinfo("Info", f"NFA loaded from '{filename}' and converted to DFA.")
            else:
                dfa_trans = {
                    st: {sym: list(tgt)[0] for sym, tgt in tr.items()}
                    for st, tr in trans.items()
                }
                self.dfa = DFA(
                    states=set(data["states"]),
                    alphabet=set(data["alphabet"]),
                    transition=dfa_trans,
                    start_state=data["start_state"],
                    final_states=set(data["final_states"])
                )
                messagebox.showinfo("Info", f"DFA loaded from '{filename}'.")

            # reset state
            self.current_index = 0
            self.current_state = self.dfa.start_state
            self.highlight_edges = None
            self.highlight_nodes = None
            self.alphabet_label.config(text=f"Valid alphabet: {', '.join(self.dfa.alphabet)}")
            self.result_label.config(text="")
            self.log_text.delete("1.0", ttk.END)
            self.table_text.delete("1.0", ttk.END)
            self.capture_transition_table()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def capture_transition_table(self):
        import io, sys as _sys
        buf = io.StringIO()
        old = _sys.stdout
        _sys.stdout = buf
        print_dfa_table(self.dfa)
        _sys.stdout = old
        self.table_text.insert(ttk.END, buf.getvalue())

    def clear_all(self):
        self.input_entry.delete(0, tk.END)
        self.result_label.config(text="")
        self.log_text.delete("1.0", ttk.END)
        self.table_text.delete("1.0", ttk.END)
        self.image_label.config(image="")
        self.alphabet_label.config(text="")

    def test_input(self):
        if not self.dfa:
            messagebox.showwarning("Warning", "Please load a DFA or NFA first.")
            return
        s = self.input_entry.get().strip()
        try:
            ok = self.dfa.accepts(s)
            self.result_label.config(text="✅ Accepted" if ok else "❌ Rejected",
                                     foreground="green" if ok else "red")
        except Exception as e:
            self.result_label.config(text=f"Error: {e}", foreground="orange")

    def step_through(self):
        if not self.dfa:
            messagebox.showwarning("Warning", "Please load a DFA or NFA first.")
            return
        # initialize
        if self.current_index == 0:
            self.input_string = self.input_entry.get().strip()
            self.current_state = self.dfa.start_state
            self.log_text.delete("1.0", ttk.END)

        if self.current_index < len(self.input_string):
            sym = self.input_string[self.current_index]
            try:
                nxt = self.dfa.transition[self.current_state][sym]
                # highlight edge and node
                self.highlight_edges = [(self.current_state, sym)]
                self.highlight_nodes = [nxt]
                visualize_dfa(
                    self.dfa,
                    view=False,
                    highlight_edges=self.highlight_edges,
                    highlight_nodes=self.highlight_nodes
                )
                self._load_graph_image()
                self.log_text.insert(tk.END,
                    f"Step {self.current_index+1}: {self.current_state} --'{sym}'--> {nxt}\n"
                )
                self.current_state = nxt
                self.current_index += 1
            except KeyError:
                self.result_label.config(
                    text=f"Error: Symbol '{sym}' not valid from state '{self.current_state}'",
                    foreground="orange"
                )
        else:
            accepted = self.current_state in self.dfa.final_states
            self.result_label.config(text="✅ Accepted" if accepted else "❌ Rejected",
                                     foreground="green" if accepted else "red")
            self.log_text.insert(tk.END, f"[CURRENT STATE] {self.current_state}\n")
            self.current_index = 0

    def render_graph(self):
        if not self.dfa:
            messagebox.showwarning("Warning", "No DFA to render.")
            return
        visualize_dfa(
            self.dfa,
            view=False,
            highlight_edges=self.highlight_edges,
            highlight_nodes=[self.current_state] if self.current_state else None
        )
        self._load_graph_image()

    def _load_graph_image(self):
        try:
            img = Image.open("dfa_graph.png")
            img.thumbnail((600,400), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    AutomataApp(root)
    root.mainloop()
