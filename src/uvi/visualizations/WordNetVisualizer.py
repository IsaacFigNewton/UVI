"""
WordNet Visualizer.

This module contains the WordNetVisualizer class for creating interactive
WordNet semantic graph visualizations with specialized coloring and tooltips.
"""

from .InteractiveVisualizer import InteractiveVisualizer


class WordNetVisualizer(InteractiveVisualizer):
    """Specialized visualizer for WordNet semantic graphs."""
    
    def __init__(self, G, hierarchy, title="WordNet Semantic Graph"):
        super().__init__(G, hierarchy, title)
    
    def get_dag_node_color(self, node):
        """Get color for a node based on type."""
        node_data = self.G.nodes.get(node, {})
        node_type = node_data.get('node_type', 'synset')
        
        if node == self.selected_node:
            return 'red'  # Highlight selected node
        elif node_type == 'category':
            return 'lightblue'    # Top-level categories
        else:
            return 'lightgreen'   # Synsets
    
    def get_node_info(self, node):
        """Get detailed information about a WordNet node."""
        if node not in self.hierarchy:
            return f"Node: {node}\nNo additional information available."
        
        data = self.hierarchy[node]
        synset_info = data.get('synset_info', {})
        node_type = synset_info.get('node_type', 'synset')
        
        if node_type == 'category':
            info = [f"WordNet Category: {node}"]
            info.append(f"Synset ID: {synset_info.get('synset_id', 'Unknown')}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            
            children = data.get('children', [])
            if children:
                if len(children) <= 3:
                    info.append(f"Children: {', '.join(children)}")
                else:
                    info.append(f"Children: {', '.join(children[:3])}")
                    info.append(f"  ... and {len(children)-3} more")
            
            definition = synset_info.get('definition', '')
            if definition:
                if len(definition) > 80:
                    definition = definition[:77] + "..."
                info.append(f"Definition: {definition}")
        else:
            # Synset node
            info = [f"WordNet Synset: {node}"]
            info.append(f"Synset ID: {synset_info.get('synset_id', 'Unknown')}")
            info.append(f"Parent: {synset_info.get('parent_category', 'Unknown')}")
            info.append(f"Depth: {data.get('depth', 'Unknown')}")
            
            definition = synset_info.get('definition', '')
            if definition:
                if len(definition) > 80:
                    definition = definition[:77] + "..."
                info.append(f"Definition: {definition}")
        
        return '\n'.join(info)
    
    def select_node(self, node):
        """Select a node and highlight it with neighbor greying."""
        self.selected_node = node
        print(f"\n=== Selected Node: {node} ===")
        print(self.get_node_info(node))
        print("=" * 40)
        
        # Use advanced highlighting instead of basic redraw
        self._highlight_node(node)
    
    def _highlight_node(self, node):
        """Highlight a selected node and grey out non-neighboring nodes."""
        import networkx as nx
        
        # Clear and redraw with highlighting
        self.ax.clear()
        
        # Get connected nodes
        predecessors = set(self.G.predecessors(node))
        successors = set(self.G.successors(node))
        connected = predecessors | successors | {node}
        
        # Draw non-connected nodes with lower alpha (greyed out)
        unconnected = set(self.G.nodes()) - connected
        if unconnected:
            nx.draw_networkx_nodes(self.G, self.pos,
                                 nodelist=list(unconnected),
                                 node_color='lightgray',
                                 node_size=1000,
                                 alpha=0.3,
                                 ax=self.ax)
        
        # Draw connected nodes with original colors
        for n in connected:
            color = self.get_dag_node_color(n)
            size = 3500 if n == node else 2000
            nx.draw_networkx_nodes(self.G, self.pos,
                                 nodelist=[n],
                                 node_color=color,
                                 node_size=size,
                                 alpha=1.0,
                                 ax=self.ax)
        
        # Draw edges
        for edge in self.G.edges():
            if edge[0] in connected and edge[1] in connected:
                nx.draw_networkx_edges(self.G, self.pos,
                                     edgelist=[edge],
                                     edge_color='red' if node in edge else 'black',
                                     width=3 if node in edge else 1.5,
                                     alpha=0.8,
                                     arrows=True,
                                     arrowsize=20,
                                     ax=self.ax)
            else:
                nx.draw_networkx_edges(self.G, self.pos,
                                     edgelist=[edge],
                                     edge_color='lightgray',
                                     width=0.5,
                                     alpha=0.2,
                                     arrows=True,
                                     ax=self.ax)
        
        # Draw labels with full synset names
        labels = {}
        for n in self.G.nodes():
            labels[n] = self._get_full_node_label(n)
        
        nx.draw_networkx_labels(self.G, self.pos,
                              labels=labels,
                              font_size=10 if n in connected else 6,
                              font_weight='bold' if n == node else 'normal',
                              ax=self.ax)
        
        self.ax.set_title(f"{self.title} - Selected: {node}", 
                         fontsize=14, fontweight='bold')
        self.ax.axis('off')
        
        # Re-add legend
        legend_elements = self.create_dag_legend()
        self.ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        self.fig.canvas.draw_idle()
    
    def _get_full_node_label(self, node):
        """Get full synset name for node labels."""
        if node not in self.hierarchy:
            return node
            
        data = self.hierarchy[node]
        synset_info = data.get('synset_info', {})
        synset_id = synset_info.get('synset_id', '')
        
        # If we have a synset ID, use it as the full label
        if synset_id and synset_id != 'Unknown':
            return synset_id
        else:
            # Fallback to node name
            return node
    
    def draw_graph(self):
        """Draw the graph with full synset names as labels."""
        import networkx as nx
        
        self.ax.clear()
        
        # Create labels with full synset names
        labels = {}
        for node in self.G.nodes():
            labels[node] = self._get_full_node_label(node)
        
        # Draw nodes with colors
        node_colors = [self.get_node_color(node) for node in self.G.nodes()]
        nx.draw_networkx_nodes(self.G, self.pos, 
                              node_color=node_colors, 
                              node_size=2000,
                              ax=self.ax)
        
        # Draw edges
        nx.draw_networkx_edges(self.G, self.pos, 
                              edge_color='black', 
                              width=1.5, 
                              alpha=0.7,
                              arrows=True,
                              arrowsize=20,
                              ax=self.ax)
        
        # Draw labels
        nx.draw_networkx_labels(self.G, self.pos, 
                               labels=labels,
                               font_size=10,
                               ax=self.ax)
        
        self.ax.set_title(self.title, fontsize=14, fontweight='bold')
        self.ax.axis('off')
        
        # Add legend
        legend_elements = self.create_dag_legend()
        self.ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    def create_dag_legend(self):
        """Create legend for WordNet visualization."""
        from matplotlib.patches import Patch
        return [
            Patch(facecolor='lightblue', label='WordNet Categories'),
            Patch(facecolor='lightgreen', label='WordNet Synsets')
        ]