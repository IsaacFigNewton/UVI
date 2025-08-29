"""
FrameNet Semantic DAG Visualization.

This script creates customizable DAG visualizations of FrameNet frame relationships with:
1. Spring-based layout with topological ordering for clear DAG structure
2. Arbitrary depth control - traverse from root frames to any depth
3. Breadth control - limit children per node for manageable visualization
4. Root frame selection - specify starting frames or auto-select interesting ones
5. Relation type filtering - include different types of semantic relationships
6. Interactive DAG exploration with hover tooltips and node selection

Command line usage:
  python semantic_graph.py --depth 4 --breadth 3
  python semantic_graph.py --roots "Motion" "Communication" --depth 2
  python semantic_graph.py --plotly --output interactive_tree.html
  python semantic_graph.py --static --relations "Inheritance" --breadth 6

Arguments:
  --depth N         Maximum depth to traverse (default: 3)
  --breadth N       Maximum children per node (default: 5)  
  --roots FRAMES    Specific root frames to start from
  --relations TYPES Relation types to include (default: Inheritance Subframe)
  --output FILE     Output filename (default: framenet_hierarchy.png)
  --no-display     Don't show the graph window
  --static          Use static DAG visualization (saves PNG automatically)
  --plotly          Use Plotly for enhanced web-based interactivity (saves HTML)
  --save-taxonomic-png  Generate additional taxonomic PNG alongside interactive mode

Interactive Features:
- Interactive Mode (default): DAG with hover tooltips, node clicking, zoom/pan (no PNG saved)
- Plotly Mode (--plotly): Web-based DAG with smooth zoom, rich hover tooltips (saves HTML)
- Static Mode (--static): Static DAG visualization for publications (saves PNG)

Visualization Types:
- DAG Layout: Spring-force positioning with topological bias (default for all modes)
- Taxonomic Layout: Hierarchical positioning by depth levels (PNG only via --save-taxonomic-png)
- Color coding: Blue=sources, Green=intermediate, Coral=sinks, Gray=isolated

Requirements:
- networkx: pip install networkx
- matplotlib: pip install matplotlib
- plotly (optional): pip install plotly

The script uses actual frame relations from frRelation.xml including:
- Inheritance relationships (781 relations)
- Using relationships (556 relations) 
- Subframe relationships (131 relations)
- And other semantic relationships for a total of 2070+ frame relations
"""

import sys
from pathlib import Path
from collections import defaultdict, deque

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

# Optional Plotly import for enhanced interactivity
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def extract_frame_hierarchy(framenet_data, max_depth=3, max_breadth=5, selected_roots=None, relation_types=None):
    """
    Extract frame hierarchy relationships from FrameNet data with configurable parameters.
    
    Args:
        framenet_data: The FrameNet corpus data
        max_depth: Maximum depth to traverse from root frames (default: 3)
        max_breadth: Maximum number of children per node to include (default: 5)
        selected_roots: List of specific root frames to start from (None = auto-select)
        relation_types: List of relation types to include (default: ['Inheritance', 'Subframe'])
        
    Returns:
        Tuple of (filtered_hierarchy, selected_root_frames)
    """
    frames = framenet_data.get('frames', {})
    frame_relations_data = framenet_data.get('frame_relations', {})
    frame_relations = frame_relations_data.get('frame_relations', [])
    
    print(f"Found {len(frame_relations)} frame relations")
    
    # Default relation types for hierarchical relationships
    if relation_types is None:
        relation_types = ['Inheritance', 'Subframe']
    
    # Build full hierarchy from frame relations data
    full_hierarchy = defaultdict(lambda: {'parents': [], 'children': [], 'depth': -1})
    
    for relation in frame_relations:
        relation_type = relation.get('type', '')
        super_frame = relation.get('superFrameName', '')
        sub_frame = relation.get('subFrameName', '')
        
        # Handle specified hierarchical relationships
        if relation_type in relation_types and super_frame and sub_frame:
            if super_frame in frames and sub_frame in frames:
                full_hierarchy[sub_frame]['parents'].append(super_frame)
                full_hierarchy[super_frame]['children'].append(sub_frame)
    
    print(f"Built hierarchy from {sum(len(data['parents']) + len(data['children']) for data in full_hierarchy.values()) // 2} relations")
    
    # Find all root frames (frames with no parents in our relation types)
    all_root_frames = []
    for frame_name in frames.keys():
        if not full_hierarchy[frame_name]['parents']:
            all_root_frames.append(frame_name)
    
    # Select root frames based on parameters
    if selected_roots is not None:
        # Use user-specified root frames
        root_frames = [f for f in selected_roots if f in frames]
        if not root_frames:
            print(f"Warning: None of the specified root frames found: {selected_roots}")
            root_frames = all_root_frames[:max_breadth]
    else:
        # Auto-select interesting root frames
        root_frames = select_interesting_roots(all_root_frames, full_hierarchy, max_breadth)
    
    print(f"Selected {len(root_frames)} root frames: {root_frames[:3]}{'...' if len(root_frames) > 3 else ''}")
    
    # BFS to build filtered hierarchy with depth and breadth limits
    filtered_hierarchy = {}
    queue = deque([(frame, 0) for frame in root_frames])
    visited = set()
    
    while queue:
        frame, depth = queue.popleft()
        
        if frame in visited or depth >= max_depth:
            continue
            
        visited.add(frame)
        
        # Add frame to filtered hierarchy
        filtered_hierarchy[frame] = {
            'depth': depth,
            'children': [],
            'parents': full_hierarchy[frame]['parents'],
            'frame_info': frames.get(frame, {})
        }
        
        # Add children within breadth limit
        children = full_hierarchy[frame]['children']
        if children and depth + 1 < max_depth:
            # Sort children by name for consistent results
            sorted_children = sorted(children)
            selected_children = sorted_children[:max_breadth]
            
            filtered_hierarchy[frame]['children'] = selected_children
            
            # Add children to queue for next level
            for child in selected_children:
                queue.append((child, depth + 1))
    
    return filtered_hierarchy, root_frames


def select_interesting_roots(all_roots, hierarchy, max_count):
    """
    Select the most interesting root frames based on their subtree size and diversity.
    
    Args:
        all_roots: List of all root frames
        hierarchy: Full hierarchy data
        max_count: Maximum number of roots to select
        
    Returns:
        List of selected root frames
    """
    if len(all_roots) <= max_count:
        return all_roots
    
    # Score roots based on subtree size and semantic diversity
    root_scores = []
    
    for root in all_roots:
        # Count descendants using BFS
        descendants = set()
        queue = deque([root])
        visited = set([root])
        
        while queue and len(descendants) < 50:  # Limit search depth
            current = queue.popleft()
            for child in hierarchy[current]['children']:
                if child not in visited:
                    descendants.add(child)
                    visited.add(child)
                    queue.append(child)
        
        # Score based on subtree size and name characteristics
        subtree_size = len(descendants)
        name_score = len(root) * 0.1  # Slight preference for longer names
        
        # Bonus for frames that sound like broad categories
        category_keywords = ['action', 'event', 'state', 'motion', 'communication', 'cognitive', 'emotion']
        category_bonus = sum(1 for keyword in category_keywords if keyword.lower() in root.lower()) * 2
        
        total_score = subtree_size + name_score + category_bonus
        root_scores.append((total_score, root))
    
    # Sort by score and return top candidates
    root_scores.sort(reverse=True)
    selected = [root for _, root in root_scores[:max_count]]
    
    print(f"Root selection scores (top 5):")
    for i, (score, root) in enumerate(root_scores[:5]):
        marker = "*" if root in selected else " "
        print(f"  {marker} {root}: {score:.1f}")
    
    return selected


def build_networkx_graph(hierarchy):
    """
    Build a NetworkX directed graph from the frame hierarchy.
    
    Args:
        hierarchy: Dict of frame relationships
        
    Returns:
        NetworkX DiGraph object
    """
    G = nx.DiGraph()
    
    # Add nodes with depth attributes
    for frame, data in hierarchy.items():
        G.add_node(frame, depth=data['depth'])
    
    # Add edges
    for frame, data in hierarchy.items():
        for child in data['children']:
            if child in hierarchy:  # Only add edge if child is in our filtered set
                G.add_edge(frame, child)
    
    return G




# Legacy wrapper functions for backward compatibility
def visualize_graph(G, hierarchy=None, title="FrameNet Frame Hierarchy", interactive=True):
    """Legacy wrapper - use FrameNetVisualizer class directly instead."""
    visualizer = FrameNetVisualizer(G, hierarchy, title)
    if interactive and hierarchy:
        interactive_graph = InteractiveFrameNetGraph(G, hierarchy, title)
        fig = interactive_graph.create_interactive_plot()
        return plt
    else:
        return visualizer.create_static_dag_visualization()


def generate_taxonomic_png(G, hierarchy, title, output_path):
    """Legacy wrapper - use FrameNetVisualizer.create_taxonomic_png() instead."""
    visualizer = FrameNetVisualizer(G, hierarchy, title)
    visualizer.create_taxonomic_png(output_path)


def main():
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='FrameNet Semantic Graph Visualization')
    parser.add_argument('--depth', type=int, default=3, help='Maximum depth to traverse (default: 3)')
    parser.add_argument('--breadth', type=int, default=5, help='Maximum children per node (default: 5)')
    parser.add_argument('--roots', nargs='*', help='Specific root frames to start from')
    parser.add_argument('--relations', nargs='*', default=['Inheritance', 'Subframe'], 
                       help='Relation types to include (default: Inheritance Subframe)')
    parser.add_argument('--output', default='framenet_hierarchy.png', help='Output filename (default: framenet_hierarchy.png)')
    parser.add_argument('--no-display', action='store_true', help='Don\'t display the graph window')
    parser.add_argument('--static', action='store_true', help='Use static visualization instead of interactive')
    parser.add_argument('--plotly', action='store_true', help='Use Plotly for enhanced web-based interactivity (requires: pip install plotly)')
    parser.add_argument('--save-taxonomic-png', action='store_true', help='Generate additional taxonomic PNG alongside interactive visualization')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("FrameNet Semantic Graph Visualization")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Max Depth: {args.depth}")
    print(f"  Max Breadth: {args.breadth}")
    print(f"  Root Frames: {args.roots or 'Auto-select'}")
    print(f"  Relation Types: {args.relations}")
    print(f"  Output File: {args.output}")
    
    # Initialize UVI and load corpora
    corpora_path = Path(__file__).parent.parent / 'corpora'
    print(f"\nInitializing UVI with corpora path: {corpora_path}")
    
    try:
        # Initialize UVI without auto-loading all corpora
        uvi = UVI(str(corpora_path), load_all=False)
        
        # Load FrameNet specifically
        print("\nLoading FrameNet corpus...")
        uvi._load_corpus('framenet')
        
        # Get corpus info to verify loading
        corpus_info = uvi.get_corpus_info()
        framenet_loaded = corpus_info.get('framenet', {}).get('loaded', False)
        
        if not framenet_loaded:
            print("ERROR: FrameNet corpus not loaded successfully")
            print("Please ensure FrameNet data is available in the corpora directory")
            return
            
        print("FrameNet loaded successfully!")
        
        # Access the FrameNet data through the corpus_loader
        framenet_data = uvi.corpus_loader.loaded_data.get('framenet', {})
        
        if not framenet_data:
            print("ERROR: No FrameNet data found")
            return
            
        frames = framenet_data.get('frames', {})
        print(f"Found {len(frames)} frames in FrameNet")
        
        # Extract frame hierarchy with configurable parameters
        print(f"\nExtracting frame hierarchy (depth={args.depth}, breadth={args.breadth})...")
        hierarchy, root_frames = extract_frame_hierarchy(
            framenet_data, 
            max_depth=args.depth,
            max_breadth=args.breadth,
            selected_roots=args.roots,
            relation_types=args.relations
        )
        
        print(f"Extracted {len(hierarchy)} frames total")
        
        # Show statistics by depth
        depth_counts = defaultdict(int)
        for frame, data in hierarchy.items():
            depth_counts[data['depth']] += 1
        
        print(f"\nFrames by depth level:")
        for depth in sorted(depth_counts.keys()):
            print(f"  Depth {depth}: {depth_counts[depth]} frames")
        
        # Build NetworkX graph
        print(f"\nBuilding NetworkX directed graph...")
        G = build_networkx_graph(hierarchy)
        
        print(f"Graph statistics:")
        print(f"  Nodes: {G.number_of_nodes()}")
        print(f"  Edges: {G.number_of_edges()}")
        print(f"  Is DAG: {nx.is_directed_acyclic_graph(G)}")
        
        # Show sample relationships
        print(f"\nSample frame relationships:")
        sample_count = 0
        for frame in root_frames[:3]:  # Show first 3 roots
            data = hierarchy.get(frame, {})
            if data.get('children'):
                print(f"  {frame} ->")
                for child in data['children'][:3]:  # Show first 3 children
                    print(f"    -> {child}")
                sample_count += 1
                if sample_count >= 3:
                    break
        
        # Create visualizer instance
        title = f"FrameNet Hierarchy (Depth: {args.depth}, Breadth: {args.breadth})"
        visualizer = FrameNetVisualizer(G, hierarchy, title)
        
        if args.plotly:
            print(f"\nCreating Plotly interactive DAG visualization...")
            
            # Save as HTML for plotly
            if args.output.endswith('.png'):
                html_output = args.output.replace('.png', '.html')
            else:
                html_output = args.output + '.html'
            
            output_path = Path(__file__).parent / html_output
            fig = visualizer.create_plotly_visualization(
                save_path=str(output_path), 
                show=not args.no_display
            )
            print(f"Saved interactive HTML to: {output_path}")
            
        else:
            interactive_mode = not args.static
            visualization_type = 'static DAG' if args.static else 'interactive DAG'
            print(f"\nCreating {visualization_type} visualization...")
            
            if args.static:
                # Static DAG visualization
                output_path = Path(__file__).parent / args.output
                plt_obj = visualizer.create_static_dag_visualization(save_path=str(output_path))
                print(f"Saved static DAG visualization to: {output_path}")
                
                # Show the plot unless disabled
                if not args.no_display:
                    print("Displaying static DAG graph...")
                    plt_obj.show()
            else:
                # Interactive DAG visualization (no PNG saved)
                interactive_graph = InteractiveFrameNetGraph(G, hierarchy, title)
                fig = interactive_graph.create_interactive_plot()
                
                # Show the plot unless disabled
                if not args.no_display:
                    print("Displaying interactive DAG graph...")
                    plt.show()
        
        # Generate taxonomic PNG if requested
        if args.save_taxonomic_png or (args.static and args.output.endswith('_taxonomic.png')):
            taxonomic_output = args.output.replace('.png', '_taxonomic.png') if not args.output.endswith('_taxonomic.png') else args.output
            taxonomic_path = Path(__file__).parent / taxonomic_output
            visualizer.create_taxonomic_png(str(taxonomic_path))
        
        print(f"\n" + "=" * 60)
        print("Semantic graph visualization completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == '__main__':
    main()