"""
Unit tests for FrameNet visualization classes.

This module contains comprehensive tests for the FrameNetVisualizer base class
and FrameNetVisualizer class to ensure proper functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import networkx as nx
from collections import defaultdict

# Import the visualization classes
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from uvi.visualizations import FrameNetVisualizer

class TestFrameNetVisualizer(unittest.TestCase):
    """Test cases for FrameNetVisualizer class."""
    
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
        
        self.interactive_graph = FrameNetVisualizer(self.G, self.hierarchy, "Interactive Test")
    
    def test_init(self):
        """Test FrameNetVisualizer initialization."""
        self.assertEqual(self.interactive_graph.G, self.G)
        self.assertEqual(self.interactive_graph.hierarchy, self.hierarchy)
        self.assertEqual(self.interactive_graph.title, "Interactive Test")
        self.assertIsNone(self.interactive_graph.selected_node)
        self.assertIsNone(self.interactive_graph.fig)
        self.assertIsNone(self.interactive_graph.ax)
        self.assertIsNone(self.interactive_graph.save_button)
    
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
    
    @patch('matplotlib.pyplot.subplots')
    def test_save_button_creation(self, mock_subplots):
        """Test save button creation in interactive plot."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_canvas = MagicMock()
        mock_fig.canvas = mock_canvas
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        # Call create_interactive_plot (this will create the button)
        result = self.interactive_graph.create_interactive_plot()
        
        # Verify that save_button attribute exists after plot creation
        self.assertIsNotNone(self.interactive_graph.save_button)
        
        # Verify figure and axes were set up correctly
        self.assertEqual(self.interactive_graph.fig, mock_fig)
        self.assertEqual(self.interactive_graph.ax, mock_ax)
    
    @patch('builtins.print')
    @patch('os.path.abspath')
    def test_save_png_functionality(self, mock_abspath, mock_print):
        """Test PNG save functionality."""
        # Mock figure
        mock_fig = MagicMock()
        mock_fig.savefig = MagicMock()
        self.interactive_graph.fig = mock_fig
        
        # Mock absolute path
        mock_abspath.return_value = "/test/path/framenet_graph_test.png"
        
        # Call save_png
        self.interactive_graph.save_png()
        
        # Verify savefig was called
        mock_fig.savefig.assert_called_once()
        
        # Check that it was called with correct parameters
        args, kwargs = mock_fig.savefig.call_args
        self.assertIn('dpi', kwargs)
        self.assertEqual(kwargs['dpi'], 300)
        self.assertEqual(kwargs['bbox_inches'], 'tight')
        self.assertEqual(kwargs['facecolor'], 'white')
        self.assertEqual(kwargs['edgecolor'], 'none')
        
        # Verify success message was printed
        mock_print.assert_called()
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        self.assertTrue(any('Graph saved as:' in call for call in print_calls))
    
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
        
        # Updated to check set_visible instead of remove since the implementation changed
        mock_annotation.set_visible.assert_called_once_with(False)
        mock_canvas.draw_idle.assert_called_once()
        self.assertIsNone(self.interactive_graph.annotation)


if __name__ == '__main__':
    unittest.main()