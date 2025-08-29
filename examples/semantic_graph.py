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


def create_demo_graph(framenet_data, num_frames=6, max_lus_per_frame=3, max_fes_per_frame=3):
    """Create a demo graph using actual FrameNet frames, their lexical units, and frame elements."""
    print(f"Creating demo graph with {num_frames} FrameNet frames, their lexical units, and frame elements...")
    
    frames_data = framenet_data.get('frames', {})
    if not frames_data:
        print("No frames data available")
        return None, {}
    
    # Select frames that have lexical units for a more interesting demo
    frames_with_lus = []
    checked_frames = 0
    
    for frame_name, frame_data in frames_data.items():
        checked_frames += 1
        lexical_units = frame_data.get('lexical_units', {})
        if isinstance(lexical_units, dict) and len(lexical_units) > 0:
            frames_with_lus.append((frame_name, len(lexical_units)))
        if len(frames_with_lus) >= num_frames * 2:  # Get more options to choose from
            break
        if checked_frames >= 100:  # Limit search to avoid long delays
            break
    
    print(f"Checked {checked_frames} frames, found {len(frames_with_lus)} frames with lexical units")
    
    # Sort by number of lexical units and take diverse set
    frames_with_lus.sort(key=lambda x: x[1], reverse=True)
    selected_frames = [name for name, _ in frames_with_lus[:num_frames]]
    
    # Fallback: if no frames with LUs found, use any frames
    if not selected_frames:
        print("No frames with lexical units found, using any available frames")
        selected_frames = list(frames_data.keys())[:num_frames]
    
    print(f"Selected frames: {selected_frames}")
    
    # Create graph and hierarchy for visualization
    G = nx.DiGraph()  # Use directed graph as expected by visualization classes
    hierarchy = {}
    
    for i, frame_name in enumerate(selected_frames):
        frame_data = frames_data[frame_name]
        lexical_units = frame_data.get('lexical_units', {})
        
        # Add frame node to graph
        G.add_node(frame_name, node_type='frame')
        
        # Create hierarchy entry for frame
        hierarchy[frame_name] = {
            'parents': [],
            'children': [],
            'frame_info': {
                'name': frame_data.get('name', frame_name),
                'definition': frame_data.get('definition', 'No definition available'),
                'id': frame_data.get('ID', 'Unknown'),
                'elements': len(frame_data.get('frame_elements', {})),
                'lexical_units': len(lexical_units),
                'node_type': 'frame'
            }
        }
        
        # Add lexical units as child nodes (if any exist)
        if lexical_units and isinstance(lexical_units, dict):
            lu_items = list(lexical_units.items())[:max_lus_per_frame]
            for j, (lu_name, lu_data) in enumerate(lu_items):
                lu_full_name = f"{lu_name}.{frame_name}"  # Make LU names unique
                
                # Add LU node to graph
                G.add_node(lu_full_name, node_type='lexical_unit')
                G.add_edge(frame_name, lu_full_name)
                
                # Create hierarchy entry for lexical unit
                hierarchy[lu_full_name] = {
                    'parents': [frame_name],
                    'children': [],
                    'frame_info': {
                        'name': lu_data.get('name', lu_name),
                        'definition': lu_data.get('definition', 'No definition available'),
                        'pos': lu_data.get('POS', 'Unknown'),
                        'frame': frame_name,
                        'node_type': 'lexical_unit'
                    }
                }
                
                # Update frame's children list
                hierarchy[frame_name]['children'].append(lu_full_name)
        
        # Add frame elements as child nodes (if any exist)
        frame_elements = frame_data.get('frame_elements', {})
        if frame_elements and isinstance(frame_elements, dict):
            fe_items = list(frame_elements.items())[:max_fes_per_frame]
            for k, (fe_name, fe_data) in enumerate(fe_items):
                fe_full_name = f"{fe_name}.{frame_name}"  # Make FE names unique
                
                # Add FE node to graph
                G.add_node(fe_full_name, node_type='frame_element')
                G.add_edge(frame_name, fe_full_name)
                
                # Create hierarchy entry for frame element
                hierarchy[fe_full_name] = {
                    'parents': [frame_name],
                    'children': [],
                    'frame_info': {
                        'name': fe_data.get('name', fe_name),
                        'definition': fe_data.get('definition', 'No definition available'),
                        'core_type': fe_data.get('coreType', 'Unknown'),
                        'id': fe_data.get('ID', 'Unknown'),
                        'frame': frame_name,
                        'node_type': 'frame_element'
                    }
                }
                
                # Update frame's children list
                hierarchy[frame_name]['children'].append(fe_full_name)
        
        # If no lexical units or frame elements exist, just leave the frame without children
        # Only use actual FrameNet data
        
        # Add some demo frame-to-frame connections for layout
        if i > 0 and i < len(selected_frames) - 1:
            prev_frame = selected_frames[i-1]
            G.add_edge(prev_frame, frame_name)
            # Update hierarchy to reflect frame relationships
            hierarchy[prev_frame]['children'].append(frame_name)
            hierarchy[frame_name]['parents'].append(prev_frame)
    
    # Calculate depths based on graph structure
    # Start from nodes with no incoming edges (roots)
    roots = [n for n in G.nodes() if G.in_degree(n) == 0]
    
    # If no clear roots, use the first node as root
    if not roots:
        roots = [selected_frames[0]]
    
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
        
        # Create demo graph with actual FrameNet frames and lexical units
        G, hierarchy = create_demo_graph(framenet_data, num_frames=5, max_lus_per_frame=2, max_fes_per_frame=2)
        
        if G is None or G.number_of_nodes() == 0:
            print("Could not create visualization graph")
            return
        
        # Show sample node information
        print(f"\\nSample node information:")
        for node in list(G.nodes())[:3]:
            frame_info = hierarchy[node]['frame_info']
            node_type = frame_info.get('node_type', 'frame')
            if node_type == 'frame':
                elements = frame_info.get('elements', 0)
                lexical_units = frame_info.get('lexical_units', 0)
                print(f"  {node} (Frame): {elements} elements, {lexical_units} lexical units")
            else:
                print(f"  {node} (Lexical Unit): {frame_info.get('pos', 'Unknown')} from {frame_info.get('frame', 'Unknown')}")
        
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