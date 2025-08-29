"""
VerbNet-FrameNet-WordNet Integrated Visualizer.

This module contains the VerbNetFrameNetWordNetVisualizer class for creating
interactive visualizations of integrated semantic graphs that link VerbNet,
FrameNet, and WordNet corpora.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Button
import networkx as nx
from typing import Dict, Any, Optional

from .Visualizer import Visualizer


class VerbNetFrameNetWordNetVisualizer(Visualizer):
    """Specialized visualizer for integrated VerbNet-FrameNet-WordNet graphs."""
    
    def __init__(self, G, hierarchy, title="Integrated Semantic Graph"):
        """
        Initialize the integrated visualizer.
        
        Args:
            G: NetworkX DiGraph containing integrated corpus nodes
            hierarchy: Hierarchy data with node information
            title: Title for visualizations
        """
        super().__init__(G, hierarchy, title)
        self.selected_node = None
        self.node_positions = None
        self.ax = None
        self.fig = None
    
    def get_dag_node_color(self, node):
        """Get color for a node based on its corpus type."""
        # Determine corpus from node prefix
        if node.startswith('VN:'):
            return '#4A90E2'  # Blue for VerbNet
        elif node.startswith('FN:'):
            return '#7B68EE'  # Purple for FrameNet
        elif node.startswith('WN:'):
            return '#50C878'  # Green for WordNet
        elif node.startswith('VERB:'):
            return '#FFB84D'  # Orange for member verbs
        else:
            return 'lightgray'  # Default
    
    def get_taxonomic_node_color(self, node):
        """Get color for taxonomic visualization based on corpus."""
        # Same as DAG colors for consistency
        return self.get_dag_node_color(node)
    
    def get_node_info(self, node):
        """Get detailed information about a node from any corpus."""
        if node not in self.hierarchy:
            return f"Node: {node}\nNo additional information available."
        
        data = self.hierarchy[node]
        info = []
        
        # Determine node type and corpus
        node_info = None
        for key in ['node_info', 'frame_info', 'synset_info', 'verb_info']:
            if key in data:
                node_info = data[key]
                break
        
        if not node_info:
            return super().get_node_info(node)
        
        node_type = node_info.get('node_type', 'unknown')
        corpus = node_info.get('corpus', '')
        
        # Format based on node type
        if node_type == 'verbnet_class':
            info.append(f"VerbNet Class: {node}")
            info.append(f"Class ID: {node_info.get('class_id', 'Unknown')}")
            
            members = node_info.get('members', [])
            if members:
                if len(members) <= 5:
                    info.append(f"Members: {', '.join(members)}")
                else:
                    info.append(f"Members: {', '.join(members[:3])}... ({len(members)} total)")
            
            themroles = node_info.get('themroles', [])
            if themroles:
                if len(themroles) <= 5:
                    info.append(f"Thematic Roles: {', '.join(themroles)}")
                else:
                    info.append(f"Thematic Roles: {len(themroles)} roles")
        
        elif node_type == 'framenet_frame':
            info.append(f"FrameNet Frame: {node}")
            info.append(f"Frame: {node_info.get('frame_name', 'Unknown')}")
            
            definition = node_info.get('definition', '')
            if definition:
                # Truncate long definitions
                if len(definition) > 100:
                    definition = definition[:97] + "..."
                info.append(f"Definition: {definition}")
            
            lexical_units = node_info.get('lexical_units', 0)
            info.append(f"Lexical Units: {lexical_units}")
        
        elif node_type == 'wordnet_synset':
            info.append(f"WordNet Synset: {node}")
            info.append(f"Synset ID: {node_info.get('synset_id', 'Unknown')}")
            
            words = node_info.get('words', [])
            if words:
                if len(words) <= 5:
                    info.append(f"Words: {', '.join(words)}")
                else:
                    info.append(f"Words: {', '.join(words[:3])}... ({len(words)} total)")
            
            definition = node_info.get('definition', '')
            if definition:
                if len(definition) > 100:
                    definition = definition[:97] + "..."
                info.append(f"Definition: {definition}")
        
        elif node_type == 'verb_member':
            info.append(f"Member Verb: {node}")
            info.append(f"Lemma: {node_info.get('lemma', 'Unknown')}")
            
            vn_class = node_info.get('verbnet_class', '')
            if vn_class:
                info.append(f"VerbNet Class: {vn_class}")
        
        else:
            return super().get_node_info(node)
        
        # Add connection information
        parents = data.get('parents', [])
        children = data.get('children', [])
        
        if parents:
            if len(parents) <= 3:
                info.append(f"Connected from: {', '.join(parents)}")
            else:
                info.append(f"Connected from: {len(parents)} nodes")
        
        if children:
            if len(children) <= 3:
                info.append(f"Connected to: {', '.join(children)}")
            else:
                info.append(f"Connected to: {len(children)} nodes")
        
        return '\n'.join(info)
    
    def create_dag_legend(self):
        """Create legend elements for integrated DAG visualization."""
        return [
            mpatches.Patch(facecolor='#4A90E2', label='VerbNet Classes'),
            mpatches.Patch(facecolor='#7B68EE', label='FrameNet Frames'),
            mpatches.Patch(facecolor='#50C878', label='WordNet Synsets'),
            mpatches.Patch(facecolor='#FFB84D', label='Member Verbs'),
            mpatches.Patch(facecolor='lightgray', label='Other Nodes')
        ]
    
    def create_taxonomic_legend(self):
        """Create legend elements for taxonomic visualization."""
        # Same as DAG legend for this integrated view
        return self.create_dag_legend()
    
    def create_interactive_plot(self):
        """Create an interactive matplotlib plot with hover and click functionality."""
        self.fig, self.ax = plt.subplots(figsize=(18, 14))
        
        # Create layout - use spring layout with adjustments for clarity
        self.node_positions = self.create_dag_layout()
        
        # Draw the graph
        self._draw_graph()
        
        # Add title and legend
        self.ax.set_title(f"{self.title}\n(VerbNet-FrameNet-WordNet Integration)", 
                         fontsize=16, fontweight='bold')
        self.ax.axis('off')
        
        # Add legend
        legend_elements = self.create_dag_legend()
        self.ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        # Add interaction instructions
        instructions = (
            "Hover: Show node details | "
            "Click: Select/highlight node | "
            "Toolbar: Zoom/Pan"
        )
        self.fig.text(0.5, 0.02, instructions, ha='center', fontsize=10, color='gray')
        
        # Add corpus labels
        self._add_corpus_labels()
        
        # Set up event handlers
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_hover)
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        
        # Add save button
        save_ax = plt.axes([0.85, 0.95, 0.1, 0.04])
        save_btn = Button(save_ax, 'Save PNG')
        save_btn.on_clicked(self._save_png)
        
        plt.tight_layout()
        return self.fig
    
    def _draw_graph(self):
        """Draw the integrated graph with corpus-specific styling."""
        # Separate nodes by corpus for different styling
        vn_nodes = [n for n in self.G.nodes() if n.startswith('VN:')]
        fn_nodes = [n for n in self.G.nodes() if n.startswith('FN:')]
        wn_nodes = [n for n in self.G.nodes() if n.startswith('WN:')]
        verb_nodes = [n for n in self.G.nodes() if n.startswith('VERB:')]
        other_nodes = [n for n in self.G.nodes() 
                      if not any(n.startswith(p) for p in ['VN:', 'FN:', 'WN:', 'VERB:'])]
        
        # Draw nodes by corpus with different styles
        if vn_nodes:
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=vn_nodes,
                                 node_color='#4A90E2',
                                 node_size=3000,
                                 node_shape='s',  # Square for VerbNet
                                 alpha=0.9,
                                 ax=self.ax)
        
        if fn_nodes:
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=fn_nodes,
                                 node_color='#7B68EE',
                                 node_size=2500,
                                 node_shape='^',  # Triangle for FrameNet
                                 alpha=0.9,
                                 ax=self.ax)
        
        if wn_nodes:
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=wn_nodes,
                                 node_color='#50C878',
                                 node_size=2500,
                                 node_shape='d',  # Diamond for WordNet
                                 alpha=0.9,
                                 ax=self.ax)
        
        if verb_nodes:
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=verb_nodes,
                                 node_color='#FFB84D',
                                 node_size=1500,
                                 node_shape='o',  # Circle for verbs
                                 alpha=0.9,
                                 ax=self.ax)
        
        if other_nodes:
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=other_nodes,
                                 node_color='lightgray',
                                 node_size=1500,
                                 alpha=0.7,
                                 ax=self.ax)
        
        # Draw edges with different styles for different connection types
        edge_colors = []
        edge_styles = []
        edge_widths = []
        
        for edge in self.G.edges(data=True):
            source, target, attrs = edge
            relation_type = attrs.get('relation_type', 'default')
            
            # Style based on connection type
            if relation_type == 'semantic_similarity':
                edge_colors.append('purple')
                edge_styles.append(':')  # Dotted for similarity
                edge_widths.append(1.5)
            elif source.startswith('VN:') and target.startswith('FN:'):
                edge_colors.append('blue')
                edge_styles.append('-')  # Solid for VN-FN
                edge_widths.append(2)
            elif source.startswith('VN:') and target.startswith('WN:'):
                edge_colors.append('green')
                edge_styles.append('-')  # Solid for VN-WN
                edge_widths.append(2)
            elif source.startswith('FN:') and target.startswith('WN:'):
                edge_colors.append('purple')
                edge_styles.append('--')  # Dashed for FN-WN
                edge_widths.append(1.5)
            else:
                edge_colors.append('gray')
                edge_styles.append('-')
                edge_widths.append(1)
        
        # Draw edges
        nx.draw_networkx_edges(self.G, self.node_positions,
                             edge_color=edge_colors,
                             width=edge_widths,
                             alpha=0.6,
                             arrows=True,
                             arrowsize=15,
                             arrowstyle='->',
                             ax=self.ax)
        
        # Draw labels with adjusted positions to avoid overlap
        label_pos = {}
        for node, (x, y) in self.node_positions.items():
            # Adjust label position based on node type
            if node.startswith('VN:'):
                label_pos[node] = (x, y - 0.08)
            elif node.startswith('FN:'):
                label_pos[node] = (x, y + 0.08)
            elif node.startswith('WN:'):
                label_pos[node] = (x + 0.08, y)
            else:
                label_pos[node] = (x, y)
        
        # Format labels (remove corpus prefix for display)
        labels = {}
        for node in self.G.nodes():
            if ':' in node:
                labels[node] = node.split(':', 1)[1]
            else:
                labels[node] = node
        
        nx.draw_networkx_labels(self.G, label_pos,
                              labels=labels,
                              font_size=8,
                              font_weight='bold',
                              ax=self.ax)
    
    def _add_corpus_labels(self):
        """Add corpus section labels to the visualization."""
        # Add text annotations to indicate corpus regions
        corpus_regions = {
            'VerbNet': '#4A90E2',
            'FrameNet': '#7B68EE',
            'WordNet': '#50C878'
        }
        
        y_offset = 0.95
        for corpus, color in corpus_regions.items():
            self.fig.text(0.02, y_offset, corpus, 
                         fontsize=12, fontweight='bold', 
                         color=color, va='top')
            y_offset -= 0.03
    
    def _on_hover(self, event):
        """Handle mouse hover events to show node information."""
        if event.inaxes != self.ax:
            return
        
        # Find closest node to mouse position
        closest_node = None
        min_dist = float('inf')
        
        for node, (x, y) in self.node_positions.items():
            dist = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
            if dist < min_dist and dist < 0.1:  # Threshold for hover detection
                min_dist = dist
                closest_node = node
        
        # Update annotation
        if closest_node:
            info = self.get_node_info(closest_node)
            # Show as tooltip (simplified for matplotlib)
            self.ax.set_title(f"{self.title}\n{info[:200]}...", fontsize=10)
        else:
            self.ax.set_title(f"{self.title}\n(VerbNet-FrameNet-WordNet Integration)", 
                            fontsize=16, fontweight='bold')
        
        self.fig.canvas.draw_idle()
    
    def _on_click(self, event):
        """Handle mouse click events to select nodes."""
        if event.inaxes != self.ax:
            return
        
        # Find clicked node
        clicked_node = None
        min_dist = float('inf')
        
        for node, (x, y) in self.node_positions.items():
            dist = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
            if dist < min_dist and dist < 0.1:
                min_dist = dist
                clicked_node = node
        
        if clicked_node:
            self.selected_node = clicked_node
            print(f"\nSelected: {clicked_node}")
            print(self.get_node_info(clicked_node))
            print("-" * 50)
            
            # Highlight selected node and its connections
            self._highlight_node(clicked_node)
    
    def _highlight_node(self, node):
        """Highlight a selected node and its connections."""
        # Clear and redraw with highlighting
        self.ax.clear()
        
        # Get connected nodes
        predecessors = set(self.G.predecessors(node))
        successors = set(self.G.successors(node))
        connected = predecessors | successors | {node}
        
        # Draw non-connected nodes with lower alpha
        unconnected = set(self.G.nodes()) - connected
        if unconnected:
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=list(unconnected),
                                 node_color='lightgray',
                                 node_size=1000,
                                 alpha=0.3,
                                 ax=self.ax)
        
        # Draw connected nodes with original colors
        for n in connected:
            color = self.get_dag_node_color(n)
            size = 3500 if n == node else 2000
            nx.draw_networkx_nodes(self.G, self.node_positions,
                                 nodelist=[n],
                                 node_color=color,
                                 node_size=size,
                                 alpha=1.0,
                                 ax=self.ax)
        
        # Draw edges
        for edge in self.G.edges():
            if edge[0] in connected and edge[1] in connected:
                nx.draw_networkx_edges(self.G, self.node_positions,
                                     edgelist=[edge],
                                     edge_color='red' if node in edge else 'black',
                                     width=3 if node in edge else 1.5,
                                     alpha=0.8,
                                     arrows=True,
                                     arrowsize=20,
                                     ax=self.ax)
            else:
                nx.draw_networkx_edges(self.G, self.node_positions,
                                     edgelist=[edge],
                                     edge_color='lightgray',
                                     width=0.5,
                                     alpha=0.2,
                                     arrows=True,
                                     ax=self.ax)
        
        # Draw labels
        labels = {}
        for n in self.G.nodes():
            if ':' in n:
                labels[n] = n.split(':', 1)[1]
            else:
                labels[n] = n
        
        nx.draw_networkx_labels(self.G, self.node_positions,
                              labels=labels,
                              font_size=10 if node in connected else 6,
                              font_weight='bold' if n == node else 'normal',
                              ax=self.ax)
        
        self.ax.set_title(f"{self.title} - Selected: {node}", 
                         fontsize=14, fontweight='bold')
        self.ax.axis('off')
        
        # Re-add legend
        legend_elements = self.create_dag_legend()
        self.ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        self.fig.canvas.draw_idle()
    
    def _save_png(self, event):
        """Save the current visualization as a PNG file."""
        filename = "integrated_vn_fn_wn_graph.png"
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Saved visualization to {filename}")