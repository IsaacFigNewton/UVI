"""
Unit tests for FrameNet visualization classes.

This module contains comprehensive tests for the FrameNetVisualizer base class
and InteractiveFrameNetGraph class to ensure proper functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import networkx as nx
from collections import defaultdict

# Import the visualization classes
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from uvi.visualizations import FrameNetVisualizer, InteractiveFrameNetGraph


class TestFrameNetVisualizer(unittest.TestCase):
    """Test cases for FrameNetVisualizer base class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test graph
        self.G = nx.DiGraph()
        self.G.add_nodes_from([
            ('Motion', {'depth': 0}),
            ('Transportation', {'depth': 1}),
            ('Vehicle_motion', {'depth': 2}),
            ('Walking', {'depth': 2})
        ])
        self.G.add_edges_from([
            ('Motion', 'Transportation'),
            ('Transportation', 'Vehicle_motion'),
            ('Transportation', 'Walking')
        ])
        
        # Create test hierarchy data
        self.hierarchy = {
            'Motion': {
                'depth': 0,
                'parents': [],
                'children': ['Transportation'],
                'frame_info': {
                    'definition': 'Frames involving physical motion or movement'
                }
            },
            'Transportation': {
                'depth': 1,
                'parents': ['Motion'],
                'children': ['Vehicle_motion', 'Walking'],
                'frame_info': {
                    'definition': 'Movement of entities from one location to another'
                }
            },
            'Vehicle_motion': {
                'depth': 2,
                'parents': ['Transportation'],
                'children': [],
                'frame_info': {
                    'definition': 'Motion involving vehicles'
                }
            },
            'Walking': {
                'depth': 2,
                'parents': ['Transportation'],
                'children': [],
                'frame_info': {
                    'definition': 'Self-propelled motion on foot'
                }
            }
        }
        
        self.visualizer = FrameNetVisualizer(self.G, self.hierarchy, "Test Frame Hierarchy")
    
    def test_init(self):
        """Test FrameNetVisualizer initialization."""
        self.assertEqual(self.visualizer.G, self.G)
        self.assertEqual(self.visualizer.hierarchy, self.hierarchy)
        self.assertEqual(self.visualizer.title, "Test Frame Hierarchy")
    
    def test_create_dag_layout(self):
        """Test DAG layout creation."""
        pos = self.visualizer.create_dag_layout()
        
        # Check that all nodes have positions
        self.assertEqual(len(pos), 4)
        for node in self.G.nodes():
            self.assertIn(node, pos)
            self.assertEqual(len(pos[node]), 2)  # x, y coordinates
    
    def test_create_taxonomic_layout(self):
        """Test taxonomic layout creation."""
        pos = self.visualizer.create_taxonomic_layout()
        
        # Check that all nodes have positions
        self.assertEqual(len(pos), 4)
        
        # Check that nodes are arranged by depth
        # Motion (depth 0) should be at y=0
        self.assertEqual(pos['Motion'][1], 0)
        
        # Transportation (depth 1) should be at y=-3
        self.assertEqual(pos['Transportation'][1], -3)
        
        # Leaf nodes (depth 2) should be at y=-6
        self.assertEqual(pos['Vehicle_motion'][1], -6)
        self.assertEqual(pos['Walking'][1], -6)
    
    def test_get_dag_node_color(self):
        """Test DAG node coloring."""
        # Test root node (no parents, has children)
        self.assertEqual(self.visualizer.get_dag_node_color('Motion'), 'lightblue')
        
        # Test intermediate node (has parents and children)
        self.assertEqual(self.visualizer.get_dag_node_color('Transportation'), 'lightgreen')
        
        # Test leaf nodes (have parents, no children)
        self.assertEqual(self.visualizer.get_dag_node_color('Vehicle_motion'), 'lightcoral')
        self.assertEqual(self.visualizer.get_dag_node_color('Walking'), 'lightcoral')
    
    def test_get_taxonomic_node_color(self):
        """Test taxonomic node coloring."""
        self.assertEqual(self.visualizer.get_taxonomic_node_color('Motion'), 'lightblue')  # depth 0
        self.assertEqual(self.visualizer.get_taxonomic_node_color('Transportation'), 'lightgreen')  # depth 1
        self.assertEqual(self.visualizer.get_taxonomic_node_color('Vehicle_motion'), 'lightyellow')  # depth 2
        self.assertEqual(self.visualizer.get_taxonomic_node_color('Walking'), 'lightyellow')  # depth 2
    
    def test_get_node_info(self):
        """Test node information retrieval."""
        info = self.visualizer.get_node_info('Motion')
        self.assertIn('Frame: Motion', info)
        self.assertIn('Depth: 0', info)
        self.assertIn('Children: Transportation', info)
        self.assertIn('Definition: Frames involving physical motion or movement', info)
        
        # Test node not in hierarchy
        info_missing = self.visualizer.get_node_info('NonExistentFrame')
        self.assertIn('NonExistentFrame', info_missing)
        self.assertIn('No additional information available', info_missing)
    
    def test_create_dag_legend(self):
        """Test DAG legend creation."""
        legend_elements = self.visualizer.create_dag_legend()
        self.assertEqual(len(legend_elements), 4)
        
        # Check that legend contains expected labels
        labels = [element.get_label() for element in legend_elements]
        expected_labels = [
            'Source Nodes (no parents)',
            'Intermediate Nodes', 
            'Sink Nodes (no children)',
            'Isolated Nodes'
        ]
        self.assertEqual(labels, expected_labels)
    
    def test_create_taxonomic_legend(self):
        """Test taxonomic legend creation."""
        legend_elements = self.visualizer.create_taxonomic_legend()
        self.assertEqual(len(legend_elements), 4)
        
        # Check that legend contains expected labels
        labels = [element.get_label() for element in legend_elements]
        expected_labels = [
            'Root Frames (Depth 0)',
            'Level 1 Frames',
            'Level 2 Frames',
            'Deeper Levels'
        ]
        self.assertEqual(labels, expected_labels)
    
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    @patch('networkx.draw_networkx_nodes')
    @patch('networkx.draw_networkx_labels') 
    @patch('networkx.draw_networkx_edges')
    def test_create_taxonomic_png(self, mock_edges, mock_labels, mock_nodes, mock_close, mock_savefig, mock_figure):
        """Test taxonomic PNG generation."""
        test_path = "test_output.png"
        
        # Mock matplotlib components
        mock_figure.return_value = MagicMock()
        
        self.visualizer.create_taxonomic_png(test_path)
        
        # Verify that matplotlib functions were called (figure gets called multiple times by matplotlib internally)
        mock_figure.assert_called()  # Changed from assert_called_once to assert_called
        mock_nodes.assert_called_once()
        mock_labels.assert_called_once() 
        mock_edges.assert_called_once()
        mock_savefig.assert_called_once_with(test_path, dpi=150, bbox_inches='tight')
        mock_close.assert_called_once()


class TestInteractiveFrameNetGraph(unittest.TestCase):
    """Test cases for InteractiveFrameNetGraph class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test graph (same as above)
        self.G = nx.DiGraph()
        self.G.add_nodes_from([
            ('Motion', {'depth': 0}),
            ('Transportation', {'depth': 1})
        ])
        self.G.add_edge('Motion', 'Transportation')
        
        self.hierarchy = {
            'Motion': {
                'depth': 0,
                'parents': [],
                'children': ['Transportation'],
                'frame_info': {'definition': 'Motion frames'}
            },
            'Transportation': {
                'depth': 1,
                'parents': ['Motion'],
                'children': [],
                'frame_info': {'definition': 'Transportation frames'}
            }
        }
        
        self.interactive_graph = InteractiveFrameNetGraph(self.G, self.hierarchy, "Interactive Test")
    
    def test_init(self):
        """Test InteractiveFrameNetGraph initialization."""
        self.assertEqual(self.interactive_graph.G, self.G)
        self.assertEqual(self.interactive_graph.hierarchy, self.hierarchy)
        self.assertEqual(self.interactive_graph.title, "Interactive Test")
        self.assertIsNone(self.interactive_graph.selected_node)
        self.assertIsNone(self.interactive_graph.fig)
        self.assertIsNone(self.interactive_graph.ax)
    
    def test_get_node_color_selected(self):
        """Test node color when selected."""
        # Test selected node
        self.interactive_graph.selected_node = 'Motion'
        self.assertEqual(self.interactive_graph.get_node_color('Motion'), 'red')
        
        # Test non-selected node
        self.assertEqual(self.interactive_graph.get_node_color('Transportation'), 'lightcoral')  # sink node
    
    def test_select_node(self):
        """Test node selection functionality."""
        with patch('builtins.print') as mock_print:
            with patch.object(self.interactive_graph, 'draw_graph') as mock_draw:
                self.interactive_graph.select_node('Motion')
                
                self.assertEqual(self.interactive_graph.selected_node, 'Motion')
                mock_print.assert_called()
                mock_draw.assert_called_once()
    
    @patch('matplotlib.pyplot.subplots')
    def test_create_interactive_plot(self, mock_subplots):
        """Test interactive plot creation."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        # Mock canvas and connect methods
        mock_canvas = MagicMock()
        mock_fig.canvas = mock_canvas
        
        result = self.interactive_graph.create_interactive_plot()
        
        # Verify setup was called
        mock_subplots.assert_called_once_with(figsize=(16, 12))
        self.assertEqual(self.interactive_graph.fig, mock_fig)
        self.assertEqual(self.interactive_graph.ax, mock_ax)
        
        # Verify event connections were made
        self.assertEqual(mock_canvas.mpl_connect.call_count, 2)
        
        self.assertEqual(result, mock_fig)
    
    def test_hide_tooltip(self):
        """Test tooltip hiding."""
        # Mock annotation
        mock_annotation = MagicMock()
        mock_fig = MagicMock()
        mock_canvas = MagicMock()
        mock_fig.canvas = mock_canvas
        
        self.interactive_graph.fig = mock_fig
        self.interactive_graph.annotation = mock_annotation
        
        self.interactive_graph.hide_tooltip()
        
        mock_annotation.remove.assert_called_once()
        mock_canvas.draw_idle.assert_called_once()
        self.assertIsNone(self.interactive_graph.annotation)


if __name__ == '__main__':
    unittest.main()