import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import matplotlib.colors as mcolors

from simulated_annealing import SimulatedAnnealing

# Create an undirected graph
G = nx.Graph()
G.add_nodes_from(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'])
G = nx.complete_graph(G)  # Create a complete graph with all possible edges
# Add weights and attraction values to edges
random.seed(777)  # For reproducibility
for(u, v) in G.edges():
    G.edges[u, v]['weight'] = random.randint(1, 32)  # Random weight between 1 and 32
    G.edges[u, v]['attraction'] = (1 / G.edges[u, v]['weight']) ** 1  # Attraction inversely proportional to weight squared
pos = nx.circular_layout(G)  # Circular layout for better visualization of complete graph

#S = SimulatedAnnealing(G.edges(), mode="best_route")
#S = SimulatedAnnealing(G.edges(), mode="current_route")
S = SimulatedAnnealing(G.edges(), mode="new_route")


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weighted Graph with Highlighted Routes")

        # Create figure
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Top frame for labels
        top_frame = ttk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Left frame for first two labels
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)

        # Right frame for last two labels
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=5)

        # Labels for route information
        self.new_route_label = tk.Label(left_frame, text="New route: ", font=('Arial', 16))
        self.new_route_label.pack(side=tk.TOP, anchor='w')

        self.current_route_label = tk.Label(left_frame, text="Current route: ", font=('Arial', 16))
        self.current_route_label.pack(side=tk.TOP, anchor='w')

        self.best_route_label = tk.Label(right_frame, text="Best route: ", font=('Arial', 16))
        self.best_route_label.pack(side=tk.TOP, anchor='w')

        self.temperature_label = tk.Label(right_frame, text="Temperature: ", font=('Arial', 16))
        self.temperature_label.pack(side=tk.TOP, anchor='w')

        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, anchor='center')

        self.btn = ttk.Button(button_frame, text="new route", command=lambda: self.callback(), width=25, padding=(10, 10))
        self.btn.pack(padx=5, pady=5)

        # Initial draw
        self.update_highlight(S.current_route[0])

    def callback(self):
        self.btn.config(state="disabled")
        S.start(self.update_highlight)

    def update_highlight(self, route):
        self.ax.clear()

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color='lightblue', node_size=500)

        # Get all edge weights and find max weight
        edge_weights = [G.edges[u, v]['weight'] for u, v in G.edges()]
        max_weight = max(edge_weights)
        min_weight = min(edge_weights)

        # Create colormap from white to red
        cmap_weight = mcolors.LinearSegmentedColormap.from_list("weight_gradient", ["black", "pink", "red", "darkred"])

        # Draw all edges with color based on weight
        for u, v in G.edges():
            weight = G.edges[u, v]['weight']
            # Normalize weight to [0, 1]
            color_val = (weight - min_weight) / (max_weight - min_weight) if max_weight > min_weight else 0.5
            edge_color = cmap_weight(color_val)
            
            # Determine edge width: thicker for higher weights
            edge_width = 1 + (weight / max_weight) * 3
            
            nx.draw_networkx_edges(G, pos, ax=self.ax, edgelist=[(u, v)], edge_color=edge_color, width=edge_width, alpha=0.8)

        # Draw node labels
        nx.draw_networkx_labels(G, pos, ax=self.ax, font_size=20, font_weight='bold')

        # Highlight selected route with flexible gradient
        if route:
            gradient_colors = ['lightblue', 'blue', 'darkblue']
            cmap = mcolors.LinearSegmentedColormap.from_list("flex_gradient", gradient_colors)
            num_edges = len(route)
            for i in range(num_edges-1):
                # Normalize index to [0,1] for colormap
                color_val = i / (num_edges - 1) if num_edges > 1 else 0.5
                color = cmap(color_val)
                nx.draw_networkx_edges(G, pos, ax=self.ax, edgelist=[(route[i], route[i+1])], edge_color=color, width=4, alpha=1)

        # Draw edge labels (on top of everything)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=self.ax, font_size=12, font_color='blue', rotate=False, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=1))

        # Adjust layout to make graph closer to edges
        self.fig.tight_layout()

        self.canvas.draw()

        # Update route information labels
        self.new_route_label.config(text=f"New route: {''.join(S.new_route[0])} (weight: {S.new_route[1]})")
        self.current_route_label.config(text=f"Current route: {''.join(S.current_route[0])} (weight: {S.current_route[1]})")
        self.best_route_label.config(text=f"Best route: {''.join(S.best_route[0])} (weight: {S.best_route[1]})")
        self.temperature_label.config(text=f"Temperature: {S.temperature:.2f}")

        self.root.update()
        self.root.update_idletasks()

def on_closing():
    root.quit()  # Stop the event loop
    root.destroy()  # Close the application

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1400x1000")
    app = GraphApp(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()