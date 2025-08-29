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
    
    def create_dag_legend(self):
        """Create legend for WordNet visualization."""
        from matplotlib.patches import Patch
        return [
            Patch(facecolor='lightblue', label='WordNet Categories'),
            Patch(facecolor='lightgreen', label='WordNet Synsets'),
            Patch(facecolor='red', label='Selected Node')
        ]