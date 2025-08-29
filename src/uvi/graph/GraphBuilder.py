"""
FrameNet Graph Builder.

This module contains the GraphBuilder class for constructing NetworkX graphs
from FrameNet data, including frames, lexical units, and frame elements.
"""

import networkx as nx
from collections import defaultdict, deque
from typing import Dict, Any, Tuple, Optional, List


class GraphBuilder:
    """Builder class for creating FrameNet semantic graphs."""
    
    def __init__(self):
        """Initialize the GraphBuilder."""
        pass
    
    def create_framenet_graph(
        self, 
        framenet_data: Dict[str, Any], 
        num_frames: int = 6, 
        max_lus_per_frame: int = 3, 
        max_fes_per_frame: int = 3
    ) -> Tuple[Optional[nx.DiGraph], Dict[str, Any]]:
        """
        Create a demo graph using actual FrameNet frames, their lexical units, and frame elements.
        
        Args:
            framenet_data: FrameNet data dictionary
            num_frames: Maximum number of frames to include
            max_lus_per_frame: Maximum lexical units per frame
            max_fes_per_frame: Maximum frame elements per frame
            
        Returns:
            Tuple of (NetworkX DiGraph, hierarchy dictionary)
        """
        print(f"Creating demo graph with {num_frames} FrameNet frames, their lexical units, and frame elements...")
        
        frames_data = framenet_data.get('frames', {})
        if not frames_data:
            print("No frames data available")
            return None, {}
        
        # Select frames that have lexical units for a more interesting demo
        selected_frames = self._select_frames_with_content(
            frames_data, num_frames
        )
        
        if not selected_frames:
            print("No suitable frames found")
            return None, {}
        
        print(f"Selected frames: {selected_frames}")
        
        # Create graph and hierarchy for visualization
        G = nx.DiGraph()  # Use directed graph as expected by visualization classes
        hierarchy = {}
        
        # Add frames and their children to the graph
        for i, frame_name in enumerate(selected_frames):
            frame_data = frames_data[frame_name]
            
            # Add frame node to graph
            G.add_node(frame_name, node_type='frame')
            
            # Create hierarchy entry for frame
            hierarchy[frame_name] = self._create_frame_hierarchy_entry(frame_data, frame_name)
            
            # Add lexical units as child nodes
            self._add_lexical_units_to_graph(
                G, hierarchy, frame_name, frame_data, max_lus_per_frame
            )
            
            # Add frame elements as child nodes
            self._add_frame_elements_to_graph(
                G, hierarchy, frame_name, frame_data, max_fes_per_frame
            )
        
        # Add demo frame-to-frame connections for layout
        self._add_frame_connections(G, hierarchy, selected_frames)
        
        # Calculate depths based on graph structure
        self._calculate_node_depths(G, hierarchy, selected_frames)
        
        # Display graph statistics
        self._display_graph_statistics(G, hierarchy)
        
        return G, hierarchy
    
    def _select_frames_with_content(
        self, 
        frames_data: Dict[str, Any], 
        num_frames: int
    ) -> List[str]:
        """Select frames that have lexical units for a more interesting demo."""
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
        
        return selected_frames
    
    def _create_frame_hierarchy_entry(
        self, 
        frame_data: Dict[str, Any], 
        frame_name: str
    ) -> Dict[str, Any]:
        """Create hierarchy entry for a frame."""
        lexical_units = frame_data.get('lexical_units', {})
        frame_elements = frame_data.get('frame_elements', {})
        
        return {
            'parents': [],
            'children': [],
            'frame_info': {
                'name': frame_data.get('name', frame_name),
                'definition': frame_data.get('definition', 'No definition available'),
                'id': frame_data.get('ID', 'Unknown'),
                'elements': len(frame_elements),
                'lexical_units': len(lexical_units),
                'node_type': 'frame'
            }
        }
    
    def _add_lexical_units_to_graph(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        frame_name: str,
        frame_data: Dict[str, Any],
        max_lus_per_frame: int
    ) -> None:
        """Add lexical units as child nodes of a frame."""
        lexical_units = frame_data.get('lexical_units', {})
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
    
    def _add_frame_elements_to_graph(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        frame_name: str,
        frame_data: Dict[str, Any],
        max_fes_per_frame: int
    ) -> None:
        """Add frame elements as child nodes of a frame."""
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
    
    def _add_frame_connections(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        selected_frames: List[str]
    ) -> None:
        """Add demo frame-to-frame connections for layout."""
        for i in range(len(selected_frames)):
            if i > 0 and i < len(selected_frames) - 1:
                prev_frame = selected_frames[i-1]
                frame_name = selected_frames[i]
                G.add_edge(prev_frame, frame_name)
                # Update hierarchy to reflect frame relationships
                hierarchy[prev_frame]['children'].append(frame_name)
                hierarchy[frame_name]['parents'].append(prev_frame)
    
    def _calculate_node_depths(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        selected_frames: List[str]
    ) -> None:
        """Calculate depths based on graph structure using BFS."""
        # Start from nodes with no incoming edges (roots)
        roots = [n for n in G.nodes() if G.in_degree(n) == 0]
        
        # If no clear roots, use the first frame as root
        if not roots:
            roots = [selected_frames[0]]
        
        # BFS to calculate depths
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
    
    def _display_graph_statistics(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any]
    ) -> None:
        """Display graph statistics and sample information."""
        print(f"Graph statistics:")
        print(f"  Nodes: {G.number_of_nodes()}")
        print(f"  Edges: {G.number_of_edges()}")
        
        # Show depth distribution
        depths = [hierarchy[node].get('depth', 0) for node in G.nodes() if node in hierarchy]
        depth_counts = {}
        for d in depths:
            depth_counts[d] = depth_counts.get(d, 0) + 1
        print(f"  Depth distribution: {dict(sorted(depth_counts.items()))}")
        
        # Show sample node information
        print(f"\nSample node information:")
        sample_nodes = list(G.nodes())[:3]
        for node in sample_nodes:
            if node in hierarchy:
                frame_info = hierarchy[node]['frame_info']
                node_type = frame_info.get('node_type', 'frame')
                if node_type == 'frame':
                    elements = frame_info.get('elements', 0)
                    lexical_units = frame_info.get('lexical_units', 0)
                    print(f"  {node} (Frame): {elements} elements, {lexical_units} lexical units")
                elif node_type == 'lexical_unit':
                    print(f"  {node} (Lexical Unit): {frame_info.get('pos', 'Unknown')} from {frame_info.get('frame', 'Unknown')}")
                elif node_type == 'frame_element':
                    print(f"  {node} (Frame Element): {frame_info.get('core_type', 'Unknown')} from {frame_info.get('frame', 'Unknown')}")