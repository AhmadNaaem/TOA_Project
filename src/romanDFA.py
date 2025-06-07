# Import necessary libraries
import tkinter as tk  # For GUI
import networkx as nx  # For creating the DFA graph
import matplotlib.pyplot as plt  # For plotting the graph
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # To embed plots in Tkinter

# Set positions for each state in the DFA
state_positions = {
    'q0': (-2, 6),
    'q1': (2, 16), 'q2': (4.5, 16), 'q3': (7.5, 16), 'q4': (11, 16),
    'q5': (2, 12), 'q6': (3.8, 12), 'q7': (6.5, 12), 'q8': (9.5, 12), 'q9': (12.5, 12),
    'q10': (0.5, 4), 'q11': (2, 5), 'q12': (2, 0), 'q13': (2, -5), 'q14': (2, -10),
    'q15': (5, -12), 'q16': (8, -12), 'q17': (11, -12), 'q18': (14, -12),
    'q19': (1, -16), 'q20': (6.5, -16), 'q21': (9.5, -16), 'q22': (12, -16),
    'q_dead': (8, 2)  # Dead state position
}

# Set of accepting states (valid final states)
accepting_states = {
    'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12',
    'q13', 'q14', 'q15', 'q16', 'q17', 'q18', 'q19', 'q20', 'q21', 'q22'
}

# Input alphabet (Roman numeral symbols)
alphabet = ['I', 'V', 'X', 'L']

# DFA transitions (state -> input symbol -> next state)
transitions = {
    'q0': {'I': 'q1', 'V': 'q5', 'X': 'q10', 'L': 'q14'},
    'q1': {'I': 'q2', 'V': 'q4', 'X': 'q9'},
    'q2': {'I': 'q3'},
    'q5': {'I': 'q6'},
    'q6': {'I': 'q7'},
    'q7': {'I': 'q8'},
    'q10': {'X': 'q11', 'L': 'q13', 'I': 'q15', 'V': 'q19'},
    'q11': {'X': 'q12', 'I': 'q15', 'V': 'q19'},
    'q12': {'I': 'q15', 'V': 'q19'},
    'q13': {'I': 'q15', 'V': 'q19'},
    'q15': {'I': 'q16', 'V': 'q18', 'X': 'q18'},
    'q16': {'I': 'q17', 'X': 'q18'},
    'q19': {'I': 'q20'},
    'q20': {'I': 'q21'},
    'q21': {'I': 'q22'},
}

# Add transitions to dead state for any missing symbol
all_states = set(state_positions)
for state in all_states:
    transitions.setdefault(state, {})  # Make sure state has a dictionary
    for symbol in alphabet:
        if symbol not in transitions[state]:
            transitions[state][symbol] = 'q_dead'  # Route to dead state
transitions['q_dead'] = {s: 'q_dead' for s in alphabet}  # Dead state loops to itself

# Create the GUI application class
class RomanDFAApp(tk.Tk):
    def __init__(self):
        super().__init__()  # Initialize the Tkinter root
        self.title("Roman Numeral DFA Validator")  # Set window title
        self.geometry("1600x900")  # Set window size
        self.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle window close

        # Create input label
        tk.Label(self, text="Enter Roman Numeral (1 to 50):", font=("Arial", 14)).pack(pady=10)
        self.entry = tk.Entry(self, font=("Arial", 14), width=20, justify='center')  # Input box
        self.entry.pack()
        tk.Button(self, text="Validate & Show Transitions", font=("Arial", 12), command=self.validate).pack(pady=10)  # Button
        self.result = tk.Label(self, text="", font=("Arial", 14))  # Label for result
        self.result.pack(pady=10)

        # Create figure and canvas for graph
        self.figure, self.ax = plt.subplots(figsize=(20, 12))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack()

        # Build and draw the DFA graph
        self.dfa_graph = self.build_dfa_graph()
        self.draw_dfa()

    def on_close(self):
        self.destroy()  # Close the app
        self.quit()  # Quit Tkinter loop

    # Convert Roman numeral to decimal value
    def roman_to_decimal(self, s):
        roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50}  # Roman to int map
        total = 0
        prev = 0
        for ch in reversed(s):  # Process from right to left
            value = roman_map[ch]
            if value < prev:
                total -= value  # Subtract if smaller than previous
            else:
                total += value  # Otherwise add
            prev = value
        return total

    # Build DFA graph using NetworkX
    def build_dfa_graph(self):
        G = nx.DiGraph()  # Create directed graph
        edge_labels = {}
        for state, edges in transitions.items():
            for symbol, target in edges.items():
                G.add_edge(state, target)  # Add edge to graph
                key = (state, target)
                if key in edge_labels:
                    edge_labels[key] += f",{symbol}"  # Append symbol if edge already exists
                else:
                    edge_labels[key] = symbol  # Create new label
        nx.set_edge_attributes(G, edge_labels, "label")  # Set labels as edge attributes
        return G

    # Draw the DFA graph
    def draw_dfa(self, highlight_path=None):
        self.ax.clear()  # Clear previous plot
        pos = {k: (v[0]*400, v[1]*400) for k, v in state_positions.items()}  # Scale positions

        # Set node colors
        node_colors = ['red' if n == 'q_dead' else 'lightgreen' if n in accepting_states else 'lightblue' for n in self.dfa_graph.nodes]

        # Draw nodes and labels
        nx.draw_networkx_nodes(self.dfa_graph, pos, ax=self.ax, node_color=node_colors, edgecolors='black')
        nx.draw_networkx_labels(self.dfa_graph, pos, ax=self.ax)

        # Highlight path if any
        edge_colors = ['blue' if highlight_path and (u, v) in highlight_path else 'gray' for u, v in self.dfa_graph.edges()]
        nx.draw_networkx_edges(self.dfa_graph, pos, ax=self.ax, edge_color=edge_colors, connectionstyle='arc3,rad=0.15')

        # Draw edge labels
        labels = {(u, v): d["label"] for u, v, d in self.dfa_graph.edges(data=True)}
        nx.draw_networkx_edge_labels(self.dfa_graph, pos, edge_labels=labels, ax=self.ax)

        self.ax.set_title("DFA for Roman Numerals (I to L)")  # Title
        self.ax.axis("off")  # Hide axes
        self.canvas.draw()  # Render the canvas

    # Validate the user input against the DFA
    def validate(self):
        input_text = self.entry.get().strip().upper()  # Get input and convert to uppercase
        state = 'q0'  # Start state
        path = []  # Track path taken
        for ch in input_text:
            if ch not in alphabet:  # Invalid character check
                self.result.config(text=f"❌ Invalid character: {ch}", fg="red")
                return
            next_state = transitions[state][ch]  # Get next state
            path.append((state, next_state))  # Add to path
            state = next_state  # Move to next state

        self.draw_dfa(highlight_path=path)  # Redraw DFA with highlighted path
        if state in accepting_states:  # Check if final state is accepting
            value = self.roman_to_decimal(input_text)  # Convert to decimal
            self.result.config(text=f"✅ '{input_text}' is valid (Decimal: {value})", fg="green")
        else:
            self.result.config(text=f"❌ '{input_text}' is not a valid Roman numeral.", fg="red")

# Run the app
if __name__ == '__main__':
    app = RomanDFAApp()
    app.mainloop()
