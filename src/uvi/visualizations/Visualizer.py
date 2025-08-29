"""
Base Visualizer Class.

This module contains the base Visualizer class that provides common functionality
for creating different types of semantic graph visualizations.
"""

from collections import defaultdict
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

# Optional Plotly import for enhanced interactivity
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class Visualizer:
    """Base class for semantic graph visualizations."""
    
    def __init__(self, G, hierarchy, title="Semantic Graph"):
        """
        Initialize the visualizer.
        
        Args:
            G: NetworkX DiGraph
            hierarchy: Hierarchy data (frame/synset structure)
            title: Title for visualizations
        """
        self.G = G
        self.hierarchy = hierarchy
        self.title = title
        
    def create_dag_layout(self):
        """Create spring-based DAG layout for the graph."""
        # Use NetworkX spring layout as base, but with DAG-aware enhancements
        pos = nx.spring_layout(self.G, k=2.5, iterations=100, seed=42)
        
        # Apply vertical bias based on topological ordering for DAG structure
        try:
            topo_order = list(nx.topological_sort(self.G))
            topo_positions = {node: i for i, node in enumerate(topo_order)}
            
            # Adjust Y coordinates to respect topological ordering while keeping spring positions
            max_topo = len(topo_order) - 1
            for node in pos:
                if node in topo_positions:
                    # Blend spring layout with topological ordering
                    spring_y = pos[node][1]
                    topo_y = 1.0 - (2.0 * topo_positions[node] / max_topo)  # Range from 1 to -1
                    
                    # Weight: 60% topological order, 40% spring layout
                    blended_y = 0.6 * topo_y + 0.4 * spring_y
                    pos[node] = (pos[node][0], blended_y)
        
        except nx.NetworkXError:
            # If not a DAG (shouldn't happen), use pure spring layout
            pass
        
        # Apply some spacing adjustments to avoid overlaps
        self._adjust_positions_for_clarity(pos)
        
        return pos
    
    def create_taxonomic_layout(self):
        """Create hierarchical layout based on depth levels."""
        # Group nodes by depth levels for hierarchical layout
        depth_nodes = defaultdict(list)
        for node, data in self.G.nodes(data=True):
            depth = data.get('depth', 0)
            depth_nodes[depth].append(node)
        
        # Create hierarchical positions
        pos = {}
        for depth, nodes in depth_nodes.items():
            n_nodes = len(nodes)
            if n_nodes == 1:
                x_positions = [0]
            else:
                # Spread nodes horizontally
                spread = min(8, n_nodes * 1.5)
                x_positions = [(i - (n_nodes-1)/2) * spread / n_nodes for i in range(n_nodes)]
            
            # Y position based on depth (negative to put roots at top)
            y = -(depth * 3)
            
            for i, node in enumerate(sorted(nodes)):
                pos[node] = (x_positions[i], y)
        
        return pos
    
    def _adjust_positions_for_clarity(self, pos):
        """Adjust positions to improve clarity and reduce overlaps."""
        nodes = list(pos.keys())
        min_distance = 0.3  # Minimum distance between nodes
        
        # Simple separation adjustment
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes[i+1:], i+1):
                x1, y1 = pos[node1]
                x2, y2 = pos[node2]
                
                distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                if distance < min_distance and distance > 0:
                    # Push nodes apart
                    dx = (x2 - x1) / distance
                    dy = (y2 - y1) / distance
                    
                    adjustment = (min_distance - distance) / 2
                    pos[node1] = (x1 - dx * adjustment, y1 - dy * adjustment)
                    pos[node2] = (x2 + dx * adjustment, y2 + dy * adjustment)
    
    def get_dag_node_color(self, node):
        """Get color for a node based on DAG properties and node type.
        
        This is a base implementation that should be overridden by subclasses
        for specialized coloring schemes.
        """
        # Check if node has type information
        node_data = self.G.nodes.get(node, {})
        node_type = node_data.get('node_type', 'default')
        
        # Basic DAG-based coloring
        in_degree = self.G.in_degree(node)
        out_degree = self.G.out_degree(node)
        
        if in_degree == 0 and out_degree > 0:
            return 'lightblue'    # Source nodes (no parents)
        elif in_degree > 0 and out_degree == 0:
            return 'lightcoral'   # Sink nodes (no children)
        elif in_degree > 0 and out_degree > 0:
            return 'lightgreen'   # Intermediate nodes
        else:
            return 'lightgray'    # Isolated nodes
    
    def get_taxonomic_node_color(self, node):
        """Get color for a node based on taxonomic depth."""
        depth = self.G.nodes[node].get('depth', 0)
        if depth == 0:
            return 'lightblue'    # Root nodes
        elif depth == 1:
            return 'lightgreen'   # Level 1 nodes
        elif depth == 2:
            return 'lightyellow'  # Level 2 nodes
        else:
            return 'lightcoral'   # Deeper levels
    
    def get_node_info(self, node):
        """Get detailed information about a node.
        
        This is a base implementation that should be overridden by subclasses
        for specialized information display.
        """
        if node not in self.hierarchy:
            return f"Node: {node}\nNo additional information available."
        
        data = self.hierarchy[node]
        info = [f"Node: {node}"]
        info.append(f"Depth: {data.get('depth', 'Unknown')}")
        
        parents = data.get('parents', [])
        if parents:
            if len(parents) <= 3:
                info.append(f"Parents: {', '.join(parents)}")
            else:
                info.append(f"Parents: {len(parents)} parent nodes")
        
        children = data.get('children', [])
        if children:
            if len(children) <= 3:
                info.append(f"Children: {', '.join(children)}")
            else:
                info.append(f"Children: {len(children)} child nodes")
        
        return '\n'.join(info)
    
    def create_dag_legend(self):
        """Create legend elements for DAG visualization.
        
        This is a base implementation that should be overridden by subclasses
        for specialized legends.
        """
        from matplotlib.patches import Patch
        return [
            Patch(facecolor='lightblue', label='Source Nodes (no parents)'),
            Patch(facecolor='lightgreen', label='Intermediate Nodes'),
            Patch(facecolor='lightcoral', label='Sink Nodes (no children)'),
            Patch(facecolor='lightgray', label='Isolated Nodes')
        ]
    
    def create_taxonomic_legend(self):
        """Create legend elements for taxonomic visualization."""
        from matplotlib.patches import Patch
        return [
            Patch(facecolor='lightblue', label='Root Nodes (Depth 0)'),
            Patch(facecolor='lightgreen', label='Level 1 Nodes'),
            Patch(facecolor='lightyellow', label='Level 2 Nodes'),
            Patch(facecolor='lightcoral', label='Deeper Levels')
        ]
    
    def create_static_dag_visualization(self, save_path=None):
        """Create a static DAG visualization using matplotlib."""
        plt.figure(figsize=(16, 12))
        
        # Create DAG layout
        pos = self.create_dag_layout()
        
        # Get node colors for DAG
        node_colors = [self.get_dag_node_color(node) for node in self.G.nodes()]
        
        # Draw graph
        nx.draw_networkx_nodes(self.G, pos, node_color=node_colors, node_size=2000, alpha=0.9)
        nx.draw_networkx_labels(self.G, pos, font_size=8, font_weight='bold')
        nx.draw_networkx_edges(self.G, pos, edge_color='gray', arrows=True, arrowsize=20, arrowstyle='->')
        
        plt.title(f"DAG {self.title}", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        # Add DAG legend
        legend_elements = self.create_dag_legend()
        plt.legend(handles=legend_elements, loc='upper right')
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return plt
    
    def create_taxonomic_png(self, save_path):
        """Generate a PNG for taxonomic (hierarchical) visualization."""
        print(f"Generating taxonomic PNG visualization...")
        
        plt.figure(figsize=(16, 12))
        
        # Create taxonomic layout
        pos = self.create_taxonomic_layout()
        
        # Get node colors for taxonomic visualization
        node_colors = [self.get_taxonomic_node_color(node) for node in self.G.nodes()]
        
        # Draw hierarchical graph
        nx.draw_networkx_nodes(self.G, pos, node_color=node_colors, node_size=2000, alpha=0.9)
        nx.draw_networkx_labels(self.G, pos, font_size=8, font_weight='bold')
        nx.draw_networkx_edges(self.G, pos, edge_color='gray', arrows=True, arrowsize=20, arrowstyle='->')
        
        plt.title(f"Taxonomic {self.title}", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        # Add taxonomic legend
        legend_elements = self.create_taxonomic_legend()
        plt.legend(handles=legend_elements, loc='upper right')
        
        # Save PNG
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved taxonomic PNG to: {save_path}")
        plt.close()
    
    def create_plotly_visualization(self, save_path=None, show=True):
        """Create an interactive Plotly visualization."""
        if not PLOTLY_AVAILABLE:
            print("Warning: Plotly not available, falling back to static visualization")
            return self.create_static_dag_visualization(save_path)
        
        # Create DAG layout
        pos = self.create_dag_layout()
        
        # Prepare node data
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        hover_text = []
        
        for node in self.G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            
            # Color by DAG properties
            node_color.append(self.get_dag_node_color(node))
            
            # Create hover text using get_node_info
            node_info = self.get_node_info(node)
            # Convert to HTML format for Plotly
            hover_info = node_info.replace('\n', '<br>')
            hover_text.append(hover_info)
        
        # Prepare edge data
        edge_x = []
        edge_y = []
        
        for edge in self.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create plotly figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='gray'),
            hoverinfo='none',
            mode='lines',
            name='Relations',
            showlegend=False
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=20,
                color=node_color,
                line=dict(width=2, color='black')
            ),
            text=node_text,
            textposition="middle center",
            textfont=dict(size=10, color='black'),
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=hover_text,
            name='Nodes',
            showlegend=False
        ))
        
        # Update layout
        fig.update_layout(
            title=dict(text=f"DAG {self.title}", x=0.5, font=dict(size=16)),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[
                dict(
                    text="Hover over nodes for details | Zoom and pan to explore",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='gray', size=10)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        # Save HTML if path provided
        if save_path:
            fig.write_html(save_path)
        
        # Show if requested
        if show:
            fig.show()
        
        return fig