"""
Interactive FrameNet Graph Visualization.

This module contains the InteractiveFrameNetGraph class that provides interactive
FrameNet semantic graph visualizations with hover, click, and zoom functionality.
"""

import networkx as nx
import matplotlib.pyplot as plt

from .FrameNetVisualizer import FrameNetVisualizer


class InteractiveFrameNetGraph(FrameNetVisualizer):
    """Interactive FrameNet graph visualization with hover, click, and zoom functionality."""
    
    def __init__(self, G, hierarchy, title="FrameNet Frame Hierarchy"):
        super().__init__(G, hierarchy, title)
        self.fig = None
        self.ax = None
        self.pos = None
        self.node_artists = None
        self.annotation = None
        self.selected_node = None
    
    def on_hover(self, event):
        """Handle mouse hover events."""
        if event.inaxes != self.ax:
            return
        
        # Find the closest node within actual node boundaries
        if self.pos and event.xdata is not None and event.ydata is not None:
            closest_node = None
            min_dist = float('inf')
            
            # Calculate appropriate hover threshold based on node size and axis limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]
            
            # Node size in data coordinates (approximate radius)
            # Default node_size is 2000, which roughly corresponds to this threshold
            hover_threshold = min(x_range, y_range) * 0.05  # Much smaller threshold
            
            for node, (x, y) in self.pos.items():
                dist = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
                if dist < hover_threshold:
                    if dist < min_dist:
                        min_dist = dist
                        closest_node = node
            
            if closest_node and closest_node != self.selected_node:
                # Show tooltip
                self.show_tooltip(event.xdata, event.ydata, closest_node)
            elif not closest_node:
                self.hide_tooltip()
    
    def on_click(self, event):
        """Handle mouse click events."""
        if event.inaxes != self.ax:
            return
        
        # Find clicked node using same precise detection as hover
        if self.pos and event.xdata is not None and event.ydata is not None:
            closest_node = None
            min_dist = float('inf')
            
            # Calculate appropriate click threshold based on node size and axis limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]
            
            # Same threshold as hover for consistency
            click_threshold = min(x_range, y_range) * 0.05
            
            for node, (x, y) in self.pos.items():
                dist = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
                if dist < click_threshold:
                    if dist < min_dist:
                        min_dist = dist
                        closest_node = node
            
            if closest_node:
                self.select_node(closest_node)
    
    def show_tooltip(self, x, y, node):
        """Show tooltip with node information."""
        if self.annotation:
            self.annotation.remove()
        
        info = self.get_node_info(node)
        self.annotation = self.ax.annotate(
            info,
            xy=(x, y),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", fc="wheat", alpha=0.8),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
            fontsize=9,
            fontweight='normal'
        )
        self.fig.canvas.draw_idle()
    
    def hide_tooltip(self):
        """Hide the tooltip."""
        if self.annotation:
            try:
                self.annotation.set_visible(False)
                self.fig.canvas.draw_idle()
            except:
                # If visibility toggle fails, try remove
                try:
                    self.annotation.remove()
                except:
                    pass
            finally:
                self.annotation = None
    
    def select_node(self, node):
        """Select a node and highlight it."""
        self.selected_node = node
        print(f"\n=== Selected Frame: {node} ===")
        print(self.get_node_info(node))
        print("=" * 40)
        
        # Redraw with highlighted selection
        self.draw_graph()
    
    def get_node_color(self, node):
        """Get color for a node based on DAG properties and selection state."""
        if node == self.selected_node:
            return 'red'  # Highlight selected node
        
        return self.get_dag_node_color(node)
    
    def draw_graph(self):
        """Draw the graph with current state."""
        self.ax.clear()
        
        # Color and size nodes based on type and selection
        node_colors = [self.get_node_color(node) for node in self.G.nodes()]
        node_sizes = []
        
        for node in self.G.nodes():
            node_data = self.G.nodes.get(node, {})
            node_type = node_data.get('node_type', 'frame')
            
            if node == self.selected_node:
                size = 3000  # Selected nodes are largest
            elif node_type == 'lexical_unit':
                size = 1000  # Lexical units are smaller
            else:
                size = 2000  # Frames are medium size
            
            node_sizes.append(size)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.G, self.pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.8,
            ax=self.ax
        )
        
        # Draw labels
        nx.draw_networkx_labels(
            self.G, self.pos,
            font_size=8,
            font_weight='bold',
            ax=self.ax
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            self.G, self.pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20,
            arrowstyle='->',
            alpha=0.6,
            ax=self.ax
        )
        
        self.ax.set_title(self.title, fontsize=16, fontweight='bold')
        self.ax.axis('off')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = self.create_dag_legend()
        legend_elements.append(Patch(facecolor='red', label='Selected Frame'))
        self.ax.legend(handles=legend_elements, loc='upper right')
    
    def create_interactive_plot(self):
        """Create the interactive matplotlib plot."""
        # Create figure and axis
        self.fig, self.ax = plt.subplots(figsize=(16, 12))
        
        # Create layout
        self.pos = self.create_dag_layout()
        
        # Initial draw
        self.draw_graph()
        
        # Connect interactive events
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Add navigation toolbar for zoom/pan
        plt.subplots_adjust(bottom=0.1)
        
        # Add instructions
        instruction_text = (
            "Instructions:\n"
            "• Hover over nodes for detailed information\n"
            "• Click on nodes to select and highlight them\n"
            "• Use toolbar to zoom and pan\n"
            "• Selected node info appears in console"
        )
        
        self.fig.text(0.02, 0.02, instruction_text, fontsize=10, 
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        return self.fig