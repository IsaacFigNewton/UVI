"""
FrameNet Interactive Semantic Graph Example.

A simple interactive visualization of FrameNet frames using NetworkX and matplotlib.
Since this FrameNet corpus doesn't include frame relations, this example demonstrates
the visualization capabilities using a small subset of actual FrameNet frames
as nodes without hierarchical connections.

This example demonstrates how to:
1. Load FrameNet data using UVI
2. Display actual frame information
3. Create an interactive graph visualization with hover tooltips and clickable nodes

Usage:
    python semantic_graph.py

Features:
- Hover over nodes to see frame details
- Click nodes to select and highlight them
- Use toolbar to zoom and pan
- Spring-force layout
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI
from uvi.visualizations import FrameNetVisualizer, InteractiveFrameNetGraph

# Import NetworkX and Matplotlib
try:
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Please install required packages: pip install networkx matplotlib")
    print(f"Error: {e}")
    sys.exit(1)


def create_demo_graph(framenet_data, num_frames=10):
    """Create a demo graph using actual FrameNet frames."""
    print(f"Creating demo graph with {num_frames} FrameNet frames...")
    
    frames_data = framenet_data.get('frames', {})
    if not frames_data:
        print("No frames data available")
        return None, {}
    
    # Select a diverse set of frames for demonstration
    frame_names = list(frames_data.keys())[:num_frames]
    print(f"Selected frames: {frame_names}")
    
    # Create graph and hierarchy for visualization
    G = nx.DiGraph()  # Use directed graph as expected by visualization classes
    hierarchy = {}
    
    for i, frame_name in enumerate(frame_names):
        frame_data = frames_data[frame_name]
        
        # Add node to graph first
        G.add_node(frame_name)
        
        # Create hierarchy entry with actual frame information
        hierarchy[frame_name] = {
            'parents': [],
            'children': [],
            'frame_info': {
                'name': frame_data.get('name', frame_name),
                'definition': frame_data.get('definition', 'No definition available'),
                'id': frame_data.get('ID', 'Unknown'),
                'elements': len(frame_data.get('frame_elements', [])),
                'lexical_units': len(frame_data.get('lexical_units', []))
            }
        }
        
        # Add some demo connections for visualization (just for layout purposes)
        if i > 0:
            prev_frame = frame_names[i-1]
            G.add_edge(prev_frame, frame_name)
            # Update hierarchy to reflect parent-child relationships
            hierarchy[prev_frame]['children'].append(frame_name)
            hierarchy[frame_name]['parents'].append(prev_frame)
    
    # Calculate depths based on graph structure
    # Start from nodes with no incoming edges (roots)
    roots = [n for n in G.nodes() if G.in_degree(n) == 0]
    
    # If no clear roots, use the first node as root
    if not roots:
        roots = [frame_names[0]]
    
    # BFS to calculate depths
    from collections import deque
    queue = deque([(root, 0) for root in roots])
    node_depths = {}
    
    while queue:
        node, depth = queue.popleft()
        if node not in node_depths:
            node_depths[node] = depth
            hierarchy[node]['depth'] = depth
            
            # Add successors to queue with incremented depth
            for successor in G.successors(node):
                if successor not in node_depths:
                    queue.append((successor, depth + 1))
    
    # Update node attributes with calculated depths
    for node, depth in node_depths.items():
        G.nodes[node]['depth'] = depth
    
    print(f"Graph statistics:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    
    # Show depth distribution
    depths = [node_depths.get(node, 0) for node in G.nodes()]
    print(f"  Depth distribution: {dict(sorted([(d, depths.count(d)) for d in set(depths)]))}")
    
    return G, hierarchy


def main():
    """Simple main function for interactive FrameNet visualization."""
    print("=" * 50)
    print("FrameNet Interactive Semantic Graph Demo")
    print("=" * 50)
    
    # Initialize UVI and load FrameNet
    corpora_path = Path(__file__).parent.parent / 'corpora'
    print(f"Loading FrameNet from: {corpora_path}")
    
    try:
        uvi = UVI(str(corpora_path), load_all=False)
        uvi._load_corpus('framenet')
        
        corpus_info = uvi.get_corpus_info()
        if not corpus_info.get('framenet', {}).get('loaded', False):
            print("ERROR: FrameNet corpus not loaded")
            return
        
        print("FrameNet loaded successfully!")
        
        # Get FrameNet data
        framenet_data = uvi.corpora_data['framenet']
        total_frames = len(framenet_data.get('frames', {}))
        print(f"Found {total_frames} frames in FrameNet")
        
        # Create demo graph with actual FrameNet frames
        G, hierarchy = create_demo_graph(framenet_data, num_frames=8)
        
        if G is None or G.number_of_nodes() == 0:
            print("Could not create visualization graph")
            return
        
        # Show sample frame information
        print(f"\\nSample frame information:")
        for node in list(G.nodes())[:3]:
            frame_info = hierarchy[node]['frame_info']
            print(f"  {node}: {frame_info['elements']} elements, {frame_info['lexical_units']} lexical units")
        
        print(f"\\nCreating interactive visualization...")
        print("Instructions:")
        print("- Hover over nodes to see frame details")
        print("- Click on nodes to select and highlight them")
        print("- Use toolbar to zoom and pan")
        print("- Close window when finished")
        
        # Create interactive visualization
        interactive_graph = InteractiveFrameNetGraph(
            G, hierarchy, "FrameNet Frames Demo"
        )
        
        fig = interactive_graph.create_interactive_plot()
        plt.show()
        
        print("\\n" + "=" * 50)
        print("Demo complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure FrameNet data is available in the corpora directory")


if __name__ == '__main__':
    main()