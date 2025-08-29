"""
FrameNet Graph Builder.

This module contains the FrameNetGraphBuilder class for constructing NetworkX graphs
from FrameNet data, including frames, lexical units, and frame elements.
"""

import networkx as nx
from collections import defaultdict
from typing import Dict, Any, Tuple, Optional, List

from .GraphBuilder import GraphBuilder


class FrameNetGraphBuilder(GraphBuilder):
    """Builder class for creating FrameNet semantic graphs."""
    
    def __init__(self):
        """Initialize the FrameNetGraphBuilder."""
        super().__init__()
    
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
        
        # Create graph and hierarchy
        G = nx.DiGraph()
        hierarchy = {}
        
        # Add frame nodes and their relationships
        self._add_frames_to_graph(
            G, hierarchy, frames_data, selected_frames
        )
        
        # Add lexical units as child nodes
        self._add_lexical_units_to_graph(
            G, hierarchy, frames_data, selected_frames, max_lus_per_frame
        )
        
        # Add frame elements as child nodes
        self._add_frame_elements_to_graph(
            G, hierarchy, frames_data, selected_frames, max_fes_per_frame
        )
        
        # Create some connections between frames for demo
        self._create_frame_connections(G, hierarchy, selected_frames)
        
        # Calculate node depths using base class method
        self.calculate_node_depths(G, hierarchy, selected_frames)
        
        # Display statistics using base class method with custom stats
        custom_stats = self.get_node_counts_by_type(G)
        self.display_graph_statistics(G, hierarchy, custom_stats)
        
        return G, hierarchy
    
    def _select_frames_with_content(
        self,
        frames_data: Dict[str, Any],
        num_frames: int
    ) -> List[str]:
        """Select frames that have lexical units for demonstration."""
        frames_with_lus = []
        frames_checked = 0
        max_checks = min(50, len(frames_data))
        
        for frame_name, frame_data in frames_data.items():
            if frames_checked >= max_checks:
                break
                
            frames_checked += 1
            lexical_units = frame_data.get('lexical_units', [])
            
            if lexical_units and len(lexical_units) > 0:
                frames_with_lus.append(frame_name)
                if len(frames_with_lus) >= num_frames:
                    break
        
        print(f"Checked {frames_checked} frames, found {len(frames_with_lus)} frames with lexical units")
        return frames_with_lus[:num_frames]
    
    def _add_frames_to_graph(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        frames_data: Dict[str, Any],
        selected_frames: List[str]
    ) -> None:
        """Add frame nodes to the graph."""
        for frame_name in selected_frames:
            frame_data = frames_data.get(frame_name, {})
            
            # Add frame node
            self.add_node_with_hierarchy(
                G, hierarchy, frame_name,
                node_type='frame',
                info={
                    'node_type': 'frame',
                    'definition': frame_data.get('definition', ''),
                    'elements': len(frame_data.get('frame_elements', [])),
                    'lexical_units': len(frame_data.get('lexical_units', []))
                }
            )
    
    def _add_lexical_units_to_graph(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        frames_data: Dict[str, Any],
        selected_frames: List[str],
        max_lus_per_frame: int
    ) -> None:
        """Add lexical unit nodes as children of frame nodes."""
        for frame_name in selected_frames:
            frame_data = frames_data.get(frame_name, {})
            lexical_units = frame_data.get('lexical_units', [])
            
            # Add limited number of lexical units
            # Note: lexical_units might be slice objects, skip if so
            if lexical_units and not isinstance(lexical_units, slice):
                try:
                    # Safely slice the lexical units
                    lu_slice = lexical_units[:max_lus_per_frame]
                    if isinstance(lu_slice, slice):
                        continue
                    
                    for i, lu in enumerate(lu_slice):
                        if isinstance(lu, slice):
                            continue
                        if isinstance(lu, dict):
                            lu_name = lu.get('name', f'lu_{i}')
                            lu_pos = lu.get('pos', 'Unknown')
                            lu_definition = lu.get('definition', '')
                        else:
                            lu_name = str(lu)
                            lu_pos = 'Unknown'
                            lu_definition = ''
                        
                        # Create unique node name
                        lu_node_name = f"{lu_name}.{frame_name}"
                        
                        # Add lexical unit node
                        self.add_node_with_hierarchy(
                            G, hierarchy, lu_node_name,
                            node_type='lexical_unit',
                            parents=[frame_name],
                            info={
                                'node_type': 'lexical_unit',
                                'name': lu_name,
                                'pos': lu_pos,
                                'definition': lu_definition,
                                'frame': frame_name
                            }
                        )
                except Exception as e:
                    print(f"Warning: Could not process lexical units for {frame_name}: {e}")
                    continue
    
    def _add_frame_elements_to_graph(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        frames_data: Dict[str, Any],
        selected_frames: List[str],
        max_fes_per_frame: int
    ) -> None:
        """Add frame element nodes as children of frame nodes."""
        for frame_name in selected_frames:
            frame_data = frames_data.get(frame_name, {})
            frame_elements = frame_data.get('frame_elements', [])
            
            # Add limited number of frame elements
            # Note: frame_elements might be slice objects, skip if so
            if frame_elements and not isinstance(frame_elements, slice):
                try:
                    # Safely slice the frame elements
                    fe_slice = frame_elements[:max_fes_per_frame]
                    if isinstance(fe_slice, slice):
                        continue
                    
                    for i, fe in enumerate(fe_slice):
                        if isinstance(fe, slice):
                            continue
                        if isinstance(fe, dict):
                            fe_name = fe.get('name', f'fe_{i}')
                            fe_core_type = fe.get('coreType', 'Unknown')
                            fe_definition = fe.get('definition', '')
                            fe_id = fe.get('ID', '')
                        else:
                            fe_name = str(fe)
                            fe_core_type = 'Unknown'
                            fe_definition = ''
                            fe_id = ''
                        
                        # Create unique node name
                        fe_node_name = f"{fe_name}@{frame_name}"
                        
                        # Add frame element node
                        self.add_node_with_hierarchy(
                            G, hierarchy, fe_node_name,
                            node_type='frame_element',
                            parents=[frame_name],
                            info={
                                'node_type': 'frame_element',
                                'name': fe_name,
                                'core_type': fe_core_type,
                                'definition': fe_definition,
                                'id': fe_id,
                                'frame': frame_name
                            }
                        )
                except Exception as e:
                    print(f"Warning: Could not process frame elements for {frame_name}: {e}")
                    continue
    
    def _create_frame_connections(
        self,
        G: nx.DiGraph,
        hierarchy: Dict[str, Any],
        selected_frames: List[str]
    ) -> None:
        """Create some demo connections between frames."""
        # Connect frames in a simple chain/hierarchy for demo purposes
        # In a real scenario, these would come from frame relations data
        for i in range(1, len(selected_frames)):
            if i == 1:
                # First connection: make second frame child of first
                self.connect_nodes(G, hierarchy, selected_frames[0], selected_frames[i])
            elif i == len(selected_frames) - 1 and len(selected_frames) > 3:
                # Last connection: connect to middle frame for more interesting structure
                mid_idx = len(selected_frames) // 2
                self.connect_nodes(G, hierarchy, selected_frames[mid_idx], selected_frames[i])
            elif i < len(selected_frames) - 1:
                # Middle frames: create a chain
                prev_frame = selected_frames[i - 1] if i % 2 == 0 else selected_frames[0]
                self.connect_nodes(G, hierarchy, prev_frame, selected_frames[i])
    
    def _display_node_info(self, node: str, hierarchy: Dict[str, Any]) -> None:
        """Display FrameNet-specific node information."""
        if node in hierarchy:
            frame_info = hierarchy[node].get('frame_info', {})
            node_type = frame_info.get('node_type', 'frame')
            
            if node_type == 'frame':
                elements = frame_info.get('elements', 0)
                lexical_units = frame_info.get('lexical_units', 0)
                print(f"  {node} (Frame): {elements} elements, {lexical_units} lexical units")
            elif node_type == 'lexical_unit':
                pos = frame_info.get('pos', 'Unknown')
                frame = frame_info.get('frame', 'Unknown')
                print(f"  {node} (Lexical Unit): {pos} from {frame}")
            elif node_type == 'frame_element':
                core_type = frame_info.get('core_type', 'Unknown')
                frame = frame_info.get('frame', 'Unknown')
                print(f"  {node} (Frame Element): {core_type} from {frame}")
            else:
                super()._display_node_info(node, hierarchy)