# Automata Simulator

A Python-based visual tool for simulating and converting finite automata (DFA/NFA with ε-transitions) with a user-friendly GUI using `ttkbootstrap`.

---

## ✨ Features

- ✅ Load DFA or NFA (supports ε-transitions) from JSON format
- 🔄 Automatically converts NFA → DFA using subset construction and epsilon-closure
- 🔍 Test input strings for acceptance (full string or step-by-step)
- 🪜 Step-by-step simulation with real-time state logs
- 🧮 Renders DFA transition table in a readable format
- 🌐 Visualizes DFA structure as a PNG graph
- 🖥️ Responsive and scrollable UI built with `Tkinter` + `ttkbootstrap`
- 🎓 Ideal for automata theory assignments and education

---

## 📦 Installation

Ensure you have Graphviz installed for graph rendering:

```bash
# Ubuntu/Debian
sudo apt install graphviz

# macOS
brew install graphviz
Also install Python dependencies (if needed):

bash
Copy
Edit
pip install -r requirements.txt
▶️ Run the App
bash
Copy
Edit
python ui/app.py
📁 Folder Structure and File Functions
graphql
Copy
Edit
automata_tools/
├── dfa/
│   ├── dfa.py            # DFA class: handles states, transitions, and string acceptance logic
│   ├── from_nfa.py       # Function to convert NFA (with ε) to DFA using subset construction
│   ├── utils.py          # Prints DFA transition table in aligned tabular format
│   └── visualize.py      # Uses Graphviz to render DFA as .png image
│
├── nfa/
│   └── nfa.py            # NFA class: handles ε-transitions, move and lambda-closure functions
│
├── ui/
│   └── app.py            # GUI Application: built using ttkbootstrap (modern Tkinter)
│                         # Features:
│                         # - Load and detect NFA/DFA
│                         # - Test/Step input string
│                         # - Render graph & show transition table
│                         # - View execution log & clear UI
│
├── examples/
│   ├── sample_dfa.json   # Example DFA input
│   ├── complex_nfa.json  # Example NFA with ε-transitions
│   └── *.json            # Your other test cases
│
└── README.md             # This file
📂 JSON Input Format
The application uses a JSON structure to represent automata. Here's a DFA sample:

json
Copy
Edit
{
  "states": ["q0", "q1", "q2"],
  "alphabet": ["0", "1"],
  "transition": {
    "q0": {"0": ["q1"], "1": ["q0"]},
    "q1": {"1": ["q2"]},
    "q2": {}
  },
  "start_state": "q0",
  "final_states": ["q2"]
}
For ε-transitions in NFAs, include "ε" as a key:

json
Copy
Edit
"q0": { "ε": ["q1", "q2"] }
🧑‍💻 User Guide
Run the app:

bash
Copy
Edit
python ui/app.py
Use the left pane:

Select a .json file from the list (loaded from examples/)

Click Load Selected File to import the automaton

Input your string (e.g., 0101)

Use the control buttons:

Test Full String – instantly check DFA acceptance

Step Through – simulate symbol-by-symbol transition

Render DFA Graph – generate and show DFA as image

Clear All – reset all fields and outputs

View results on the right:

🖼 DFA graph (PNG)

📜 Execution log

📋 Transition table

📸 Screenshots
Add screenshots here after capturing them during usage:

scss
Copy
Edit
![Main GUI](demo/screenshot_ui.png)
![Step Simulation](demo/step_example.png)
🛠 Technical Notes
Uses ttkbootstrap: a modern wrapper for ttk (supports themes, colors)

Uses Pillow to embed images (PNG) inside the GUI

GUI supports interactive exploration of automata behavior

Detects DFA vs. NFA format based on ε-transitions automatically

Conversion and logic are fully modular (usable via CLI if desired)

🧪 Bonus / Testing Tips
You can add more test files to the examples/ folder

Use edge cases like unreachable states, nondeterministic transitions, or ε-loops

Consider printing or asserting behavior for known accepted/rejected strings

📜 License
MIT License — Developed by Bui Quang Minh
Vietnamese-German University | Student ID: 10423075