"""
Interactive Visualizer.

This module contains the InteractiveVisualizer class that adds interactive functionality
to the base Visualizer class, providing hover, click, and zoom functionality.
"""

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import datetime
import os

from .Visualizer import Visualizer
from .VisualizerConfig import VisualizerConfig


class InteractiveVisualizer(Visualizer):
    """Interactive visualization with hover, click, and zoom functionality."""
    
    def __init__(self, G, hierarchy, title="Interactive Semantic Graph"):
        super().__init__(G, hierarchy, title)
        self.fig = None
        self.ax = None
        self.pos = None
        self.node_artists = None
        self.annotation = None
        self.selected_node = None
        # save_button removed - use matplotlib toolbar for saving
    
    def on_hover(self, event):
        """Handle mouse hover events using consolidated interaction handling."""
        closest_node = self._handle_node_interaction_events(event, 'hover')
        
        if closest_node and closest_node != self.selected_node:
            # Show tooltip
            self.show_tooltip(event.xdata, event.ydata, closest_node)
        elif not closest_node:
            self.hide_tooltip()
    
    def on_click(self, event):
        """Handle mouse click events using consolidated interaction handling."""
        closest_node = self._handle_node_interaction_events(event, 'click')
        
        if closest_node:
            self.select_node(closest_node)
    
    def show_tooltip(self, x, y, node):
        """Show tooltip with node information using standardized styling."""
        if self.annotation:
            self.annotation.remove()
        
        info = self.get_node_info(node)
        tooltip_style = self._get_tooltip_styling()
        
        self.annotation = self.ax.annotate(
            info,
            xy=(x, y),
            xytext=tooltip_style['offset'],
            textcoords="offset points",
            bbox=tooltip_style['bbox'],
            arrowprops=tooltip_style['arrowprops'],
            fontsize=tooltip_style['fontsize'],
            fontweight=tooltip_style['fontweight']
        )
        self.fig.canvas.draw_idle()
    
    def _get_tooltip_styling(self):
        """Get standardized tooltip styling from centralized configuration."""
        visualizer_type = self._get_visualizer_type()
        tooltip_type = 'combined' if 'combined' in visualizer_type.lower() else 'default'
        return VisualizerConfig.get_tooltip_style(tooltip_type)
    
    def hide_tooltip(self):
        """Hide the tooltip."""
        if self.annotation:
            try:
                self.annotation.set_visible(False)
                self.fig.canvas.draw_idle()
            except:
                # If visibility toggle fails, try remove
                try:
                    self.annotation.remove()
                except:
                    pass
            finally:
                self.annotation = None
    
    def select_node(self, node):
        """Select a node and highlight it."""
        self.selected_node = node
        print(f"\n=== Selected Node: {node} ===")
        print(self.get_node_info(node))
        print("=" * 40)
        
        # Use advanced highlighting for better visual feedback
        self._highlight_connected_nodes(node)
    
    
    def get_node_color(self, node):
        """Get color for a node based on DAG properties and selection state."""
        if node == self.selected_node:
            return 'red'  # Highlight selected node
        
        return self.get_dag_node_color(node)
    
    def draw_graph(self):
        """
        Template method for drawing the graph with standardized structure.
        
        This method provides a consistent drawing pipeline with customization hooks:
        1. Prepare drawing (clear axes, setup)
        2. Draw nodes (with customizable styling)
        3. Draw edges (with customizable styling)  
        4. Draw labels (with customizable formatting)
        5. Finalize drawing (title, legend, axis configuration)
        """
        # Step 1: Prepare drawing
        self._prepare_drawing()
        
        # Step 2: Draw nodes with customizable styling
        self._draw_nodes()
        
        # Step 3: Draw edges with customizable styling
        self._draw_edges()
        
        # Step 4: Draw labels with customizable formatting
        self._draw_labels()
        
        # Step 5: Finalize drawing
        self._finalize_drawing()
    
    def _prepare_drawing(self):
        """Prepare the drawing canvas. Override for custom preparation steps."""
        self.ax.clear()
    
    def _draw_nodes(self):
        """Draw nodes with standardized styling. Override for custom node rendering."""
        # Get node styling configuration
        node_colors = []
        node_sizes = []
        node_alphas = []
        
        config = VisualizerConfig.create_visualizer_config(self._get_visualizer_type())
        
        for node in self.G.nodes():
            # Get color (delegates to subclass-specific logic)
            node_colors.append(self.get_node_color(node))
            
            # Get size based on node type and selection
            size = self._get_node_size(node, config)
            node_sizes.append(size)
            
            # Get alpha value
            alpha = self._get_node_alpha(node, config)
            node_alphas.append(alpha)
        
        # Draw all nodes at once for efficiency
        nx.draw_networkx_nodes(
            self.G, self.pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.8,  # Default alpha, could be made configurable per node
            ax=self.ax
        )
    
    def _get_node_size(self, node, config):
        """Get node size based on node type and selection state."""
        node_data = self.G.nodes.get(node, {})
        node_type = node_data.get('node_type', 'default')
        node_sizes = config['node_sizes']
        
        if node == self.selected_node:
            return node_sizes['selected']
        elif node_type == 'lexical_unit':
            return node_sizes['lexical_unit']
        elif node_type == 'frame_element':
            return node_sizes['frame_element']
        else:
            return node_sizes['connected']  # Default size
    
    def _get_node_alpha(self, node, config):
        """Get node alpha based on state. Override for custom alpha logic."""
        return config['alpha_values']['connected_nodes']
    
    def _draw_edges(self):
        """Draw edges with standardized styling. Override for custom edge rendering."""
        config = VisualizerConfig.create_visualizer_config(self._get_visualizer_type())
        edge_style = config['edge_styles']
        
        nx.draw_networkx_edges(
            self.G, self.pos,
            edge_color='gray',  # Default color
            arrows=True,
            arrowsize=edge_style['arrow_size'],
            arrowstyle='->',
            alpha=0.6,
            ax=self.ax
        )
    
    def _draw_labels(self):
        """Draw labels with standardized styling. Override for custom label rendering."""
        config = VisualizerConfig.create_visualizer_config(self._get_visualizer_type())
        font_style = config['font_styles']
        
        # Create labels using the formatting method (allows subclass customization)
        labels = {}
        for node in self.G.nodes():
            labels[node] = self._format_node_label(node)
        
        nx.draw_networkx_labels(
            self.G, self.pos,
            labels=labels,
            font_size=8,  # Could be made configurable
            font_weight='bold',
            ax=self.ax
        )
    
    def _finalize_drawing(self):
        """Finalize the drawing with title, legend, and axis configuration."""
        # Set title
        self.ax.set_title(self.title, fontsize=16, fontweight='bold')
        self.ax.axis('off')
        
        # Add legend using standardized approach
        legend_elements = self._create_standardized_legend()
        if legend_elements:
            config = VisualizerConfig.get_legend_config()
            self.ax.legend(
                handles=legend_elements, 
                loc=config['location'],
                fontsize=config['fontsize']
            )
    
    def _create_standardized_legend(self):
        """
        Create standardized legend elements.
        
        This method consolidates legend creation logic and provides
        a consistent approach across all visualizers.
        """
        legend_elements = []
        
        # Add DAG-specific legend elements
        dag_elements = self.create_dag_legend()
        legend_elements.extend(dag_elements)
        
        # Add selection indicator if a node is selected
        if self.selected_node:
            from matplotlib.patches import Patch
            legend_elements.append(Patch(facecolor='red', label='Selected Node'))
        
        return legend_elements
    
    def create_interactive_plot(self):
        """Create the interactive matplotlib plot."""
        # Create figure and axis
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        
        # Create layout
        self.pos = self.create_dag_layout()
        
        # Initial draw
        self.draw_graph()
        
        # Connect interactive events
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Add navigation toolbar for zoom/pan
        plt.subplots_adjust(bottom=0.10)  # Make room for instructions
        
        # Add instructions
        instruction_text = (
            "Hover: Show node details | "
            "Click: Select/highlight node | "
            "Toolbar: Zoom/Pan"
        )
        
        self.fig.text(0.02, 0.02, instruction_text, fontsize=10, 
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        return self.fig
    
    def _highlight_connected_nodes(self, node, custom_styling=None):
        """
        Highlight a selected node and grey out non-neighboring nodes.
        
        This consolidated method replaces identical implementations across
        FrameNet, VerbNet, and WordNet visualizers.
        
        Args:
            node: The node to highlight
            custom_styling: Optional dict with custom styling parameters
        """
        import networkx as nx
        
        # Clear and redraw with highlighting
        self.ax.clear()
        
        # Get connected nodes
        predecessors = set(self.G.predecessors(node))
        successors = set(self.G.successors(node))
        connected = predecessors | successors | {node}
        
        # Get styling configuration
        styling = self._get_highlight_styling(custom_styling)
        
        # Draw non-connected nodes with lower alpha (greyed out)
        unconnected = set(self.G.nodes()) - connected
        if unconnected:
            nx.draw_networkx_nodes(self.G, self.pos,
                                 nodelist=list(unconnected),
                                 node_color=styling['unconnected_color'],
                                 node_size=styling['unconnected_size'],
                                 alpha=styling['unconnected_alpha'],
                                 ax=self.ax)
        
        # Draw connected nodes with original colors
        for n in connected:
            color = self.get_dag_node_color(n)
            size = styling['selected_size'] if n == node else styling['connected_size']
            nx.draw_networkx_nodes(self.G, self.pos,
                                 nodelist=[n],
                                 node_color=color,
                                 node_size=size,
                                 alpha=styling['connected_alpha'],
                                 ax=self.ax)
        
        # Draw edges with highlighting
        self._draw_highlighted_edges(node, connected, styling)
        
        # Draw labels with customizable formatting
        self._draw_highlighted_labels(node, connected, styling)
        
        # Update title and legend
        self.ax.set_title(f"{self.title} - Selected: {node}", 
                         fontsize=14, fontweight='bold')
        self.ax.axis('off')
        
        # Re-add legend
        legend_elements = self.create_dag_legend()
        self.ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        self.fig.canvas.draw_idle()
    
    def _get_highlight_styling(self, custom_styling=None):
        """Get styling configuration for node highlighting from centralized config."""
        # Get visualizer type for configuration
        visualizer_type = self._get_visualizer_type()
        
        # Get styling from centralized configuration
        styling = VisualizerConfig.get_highlight_styling(visualizer_type, custom_styling)
        
        return styling
    
    def _get_visualizer_type(self):
        """Get the visualizer type for configuration purposes. Override in subclasses."""
        return 'default'
    
    def _draw_highlighted_edges(self, selected_node, connected_nodes, styling):
        """Draw edges with highlighting for selected node."""
        import networkx as nx
        
        for edge in self.G.edges():
            if edge[0] in connected_nodes and edge[1] in connected_nodes:
                # Connected edges (highlighted or normal)
                nx.draw_networkx_edges(self.G, self.pos,
                                     edgelist=[edge],
                                     edge_color=styling['edge_highlight_color'] if selected_node in edge else styling['edge_normal_color'],
                                     width=styling['edge_highlight_width'] if selected_node in edge else styling['edge_normal_width'],
                                     alpha=styling['edge_highlight_alpha'],
                                     arrows=True,
                                     arrowsize=20,
                                     ax=self.ax)
            else:
                # Greyed out edges
                nx.draw_networkx_edges(self.G, self.pos,
                                     edgelist=[edge],
                                     edge_color=styling['edge_greyed_color'],
                                     width=styling['edge_greyed_width'],
                                     alpha=styling['edge_greyed_alpha'],
                                     arrows=True,
                                     ax=self.ax)
    
    def _draw_highlighted_labels(self, selected_node, connected_nodes, styling):
        """Draw labels with highlighting. Can be overridden for custom label formatting."""
        import networkx as nx
        
        labels = {}
        for n in self.G.nodes():
            labels[n] = self._format_node_label(n)
        
        nx.draw_networkx_labels(self.G, self.pos,
                              labels=labels,
                              font_size=styling['font_size_connected'] if n in connected_nodes else styling['font_size_unconnected'],
                              font_weight=styling['font_weight_selected'] if n == selected_node else styling['font_weight_normal'],
                              ax=self.ax)
    
    def _format_node_label(self, node):
        """Format node label. Override in subclasses for custom formatting."""
        return str(node)
    
    def _get_interaction_thresholds(self):
        """Get interaction thresholds for hover and click detection from centralized config."""
        # Get threshold percentages from configuration
        thresholds_config = VisualizerConfig.get_interaction_thresholds()
        
        # If axes are not set up yet, return default values
        if self.ax is None:
            return {
                'hover_threshold': thresholds_config['hover_threshold'],
                'click_threshold': thresholds_config['click_threshold']
            }
        
        try:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]
            
            return {
                'hover_threshold': min(x_range, y_range) * thresholds_config['hover_threshold'],
                'click_threshold': min(x_range, y_range) * thresholds_config['click_threshold']
            }
        except:
            # Fallback to default values if axis limits are not available
            return {
                'hover_threshold': thresholds_config['hover_threshold'],
                'click_threshold': thresholds_config['click_threshold']
            }
    
    def _handle_node_interaction_events(self, event, interaction_type='hover'):
        """
        Consolidated node interaction event handling.
        
        Args:
            event: The matplotlib event
            interaction_type: 'hover' or 'click'
            
        Returns:
            The closest node within interaction threshold, or None
        """
        if event.inaxes != self.ax or not self.pos:
            return None
        
        if event.xdata is None or event.ydata is None:
            return None
            
        thresholds = self._get_interaction_thresholds()
        threshold = thresholds[f'{interaction_type}_threshold']
        
        closest_node = None
        min_dist = float('inf')
        
        for node, (x, y) in self.pos.items():
            dist = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
            if dist < threshold:
                if dist < min_dist:
                    min_dist = dist
                    closest_node = node
        
        return closest_node