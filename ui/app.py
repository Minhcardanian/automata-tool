import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, scrolledtext, Listbox
from PIL import Image, ImageTk
import json
import os
import sys

# allow imports from parent
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

from dfa.dfa import DFA
from dfa.from_nfa import nfa_to_dfa
from dfa.utils import print_dfa_table
from dfa.visualize import visualize_dfa
from nfa.nfa import NFA
from main import is_probably_nfa

class AutomataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automata Simulator")
        self.root.configure(bg="#f9f9f9")

        # base paths
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.examples_dir = os.path.join(self.base_dir, 'examples')
        self.graph_path = os.path.join(self.base_dir, 'dfa_graph.png')

        # ---- outer horizontal pane: controls | right_pane ----
        self.h_pane = ttk.PanedWindow(root, orient=HORIZONTAL)
        self.h_pane.pack(fill="both", expand=True)

        # left controls frame
        self.ctrl_frame = ttk.Frame(self.h_pane, width=240)
        self.h_pane.add(self.ctrl_frame, weight=0)

        # right vertical pane: logs/table over graph
        self.v_pane = ttk.PanedWindow(self.h_pane, orient=VERTICAL)
        self.h_pane.add(self.v_pane, weight=1)

        # top-right: logs + table
        self.log_frame = ttk.Frame(self.v_pane, height=220)
        self.v_pane.add(self.log_frame, weight=0)

        # bottom-right: graph
        self.graph_frame = ttk.Frame(self.v_pane)
        self.v_pane.add(self.graph_frame, weight=1)

        # automaton state
        self.dfa = None
        self.input_string = ""
        self.current_index = 0
        self.current_state = None
        self.highlight_edges = None
        self.highlight_nodes = None

        self.build_gui()

    def build_gui(self):
        # --- Controls (in ctrl_frame) ---
        lf = ttk.LabelFrame(self.ctrl_frame, text="File Loader")
        lf.pack(fill="x", pady=(5, 10))
        ttk.Label(lf, text="Select JSON file:").pack(side=LEFT, padx=5)
        self.file_list = Listbox(lf, height=5, width=28)
        self.file_list.pack(side=LEFT)
        self.populate_file_list()
        ttk.Button(
            lf,
            text="Load Selected File",
            bootstyle="primary",
            command=self.load_selected_file
        ).pack(side=LEFT, padx=8)

        ttk.Label(self.ctrl_frame, text="Enter input string:").pack(anchor="w", pady=(0, 2))
        self.input_entry = ttk.Entry(self.ctrl_frame)
        self.input_entry.pack(fill="x", pady=(0, 8))
        self.alphabet_label = ttk.Label(self.ctrl_frame, text="", font=("Arial", 9))
        self.alphabet_label.pack(anchor="w", pady=(0, 12))

        ttk.Button(
            self.ctrl_frame,
            text="Test Full String",
            bootstyle="primary",
            command=self.test_input
        ).pack(fill="x", pady=4)
        ttk.Button(
            self.ctrl_frame,
            text="Step Through",
            bootstyle="primary",
            command=self.step_through
        ).pack(fill="x", pady=4)
        self.result_label = ttk.Label(self.ctrl_frame, text="", font=("Arial", 14, "bold"))
        self.result_label.pack(pady=10)
        ttk.Button(
            self.ctrl_frame,
            text="Render DFA Graph",
            bootstyle="primary",
            command=self.render_graph
        ).pack(fill="x", pady=(0, 8))

        # --- Logs & Table (in log_frame) ---
        ttk.Label(
            self.log_frame,
            text="Execution Log:",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=5, pady=(5, 2))
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            height=6,
            width=60,
            bg="#fff"
        )
        self.log_text.pack(fill="both", expand=False, padx=5, pady=(0, 8))

        ttk.Label(
            self.log_frame,
            text="Transition Table:",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=5, pady=(0, 2))
        self.table_text = scrolledtext.ScrolledText(
            self.log_frame,
            height=8,
            width=60,
            bg="#fff"
        )
        self.table_text.pack(fill="both", expand=False, padx=5, pady=(0, 8))

        ttk.Button(
            self.log_frame,
            text="Clear All",
            bootstyle="danger",
            command=self.clear_all
        ).pack(anchor="e", padx=5, pady=(0, 5))

        # --- Graph (in graph_frame) ---
        self.image_label = ttk.Label(self.graph_frame)
        self.image_label.pack(fill="both", expand=True, padx=5, pady=5)

    def populate_file_list(self):
        self.file_list.delete(0, tk.END)
        for f in os.listdir(self.examples_dir):
            if f.endswith(".json"):
                self.file_list.insert(tk.END, f)

    def load_selected_file(self):
        sel = self.file_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "No file selected.")
            return
        fname = self.file_list.get(sel[0])
        path = os.path.join(self.examples_dir, fname)
        try:
            with open(path) as f:
                data = json.load(f)
            # build transition
            trans = {
                s: {
                    sym: set(tgt if isinstance(tgt, list) else [tgt])
                    for sym, tgt in m.items()
                }
                for s, m in data["transition"].items()
            }
            # detect NFA
            if is_probably_nfa(path):
                nfa = NFA(
                    states=set(data["states"]),
                    alphabet=set(data["alphabet"]),
                    transition=trans,
                    start_state=data["start_state"],
                    final_states=set(data["final_states"])
                )
                self.dfa = nfa_to_dfa(nfa)
                messagebox.showinfo("Info", f"NFA → DFA loaded from '{fname}'.")
            else:
                dfa_trans = {
                    s: {sym: list(tgt)[0] for sym, tgt in m.items()}
                    for s, m in trans.items()
                }
                self.dfa = DFA(
                    states=set(data["states"]),
                    alphabet=set(data["alphabet"]),
                    transition=dfa_trans,
                    start_state=data["start_state"],
                    final_states=set(data["final_states"])
                )
                messagebox.showinfo("Info", f"DFA loaded from '{fname}'.")
            # reset state
            self.current_index = 0
            self.current_state = self.dfa.start_state
            self.highlight_edges = None
            self.highlight_nodes = None
            self.alphabet_label.config(
                text=f"Valid alphabet: {', '.join(self.dfa.alphabet)}"
            )
            self.result_label.config(text="")
            self.log_text.delete("1.0", tk.END)
            self.table_text.delete("1.0", tk.END)
            self.capture_transition_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")

    def capture_transition_table(self):
        import io
        import sys as _sys
        buf = io.StringIO()
        old = _sys.stdout
        _sys.stdout = buf
        print_dfa_table(self.dfa)
        _sys.stdout = old
        self.table_text.insert(tk.END, buf.getvalue())

    def clear_all(self):
        self.input_entry.delete(0, tk.END)
        self.result_label.config(text="")
        self.log_text.delete("1.0", tk.END)
        self.table_text.delete("1.0", tk.END)
        self.image_label.config(image='')
        self.image_label.image = None
        self.current_index = 0
        self.current_state = self.dfa.start_state if self.dfa else None
        self.highlight_edges = None
        self.highlight_nodes = None

    def test_input(self):
        if not self.dfa:
            messagebox.showwarning("Warning", "Load an automaton first.")
            return
        s = self.input_entry.get().strip()
        # invalid-symbol check
        for ch in s:
            if ch not in self.dfa.alphabet:
                self.result_label.config(
                    text=f"Error: '{ch}' not in alphabet",
                    foreground="orange"
                )
                return
        try:
            ok = self.dfa.accepts(s)
            self.result_label.config(
                text="✅ Accepted" if ok else "❌ Rejected",
                foreground="green" if ok else "red"
            )
        except Exception as e:
            self.result_label.config(text=f"Error: {e}", foreground="orange")

    def step_through(self):
        if not self.dfa:
            messagebox.showwarning("Warning", "Load an automaton first.")
            return
        if self.current_index == 0:
            self.input_string = self.input_entry.get().strip()
            self.current_state = self.dfa.start_state
            self.log_text.delete("1.0", tk.END)
        if self.current_index < len(self.input_string):
            sym = self.input_string[self.current_index]
            try:
                nxt = self.dfa.transition[self.current_state][sym]
                self.highlight_edges = [(self.current_state, sym)]
                self.highlight_nodes = [nxt]
                visualize_dfa(
                    self.dfa,
                    view=False,
                    filename=self.graph_path[:-4],
                    highlight_edges=self.highlight_edges,
                    highlight_nodes=self.highlight_nodes
                )
                self._load_graph_image()
                self.log_text.insert(
                    tk.END,
                    f"Step {self.current_index+1}: "
                    f"{self.current_state} --'{sym}'--> {nxt}\n"
                )
                self.current_state = nxt
                self.current_index += 1
                if self.current_index == len(self.input_string):
                    self._finish_run()
            except KeyError:
                self.result_label.config(
                    text=f"Error: '{sym}' not valid from {self.current_state}",
                    foreground="orange"
                )
        else:
            self._finish_run()

    def _finish_run(self):
        fin = self.current_state in self.dfa.final_states
        self.result_label.config(
            text="✅ Accepted" if fin else "❌ Rejected",
            foreground="green" if fin else "red"
        )
        self.log_text.insert(tk.END, f"[CURRENT STATE] {self.current_state}\n")
        self.current_index = 0
        self.render_graph()

    def render_graph(self):
        if not self.dfa:
            messagebox.showwarning("Warning","No DFA to render."); 
            return
        
        visualize_dfa(
            self.dfa,
            view=False,
            filename=self.graph_path[:-4],
            highlight_edges=self.highlight_edges,
            highlight_nodes=[self.current_state] if self.current_state else None
        )
        self._load_graph_image()

    def _load_graph_image(self):
        try:
            img = Image.open(self.graph_path)
            img.thumbnail((800, 400), Image.Resampling.LANCZOS)
            tkimg = ImageTk.PhotoImage(img)
            self.image_label.config(image=tkimg)
            self.image_label.image = tkimg
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    AutomataApp(root)
    root.mainloop()
