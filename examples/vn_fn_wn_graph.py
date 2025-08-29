"""
Integrated VerbNet-FrameNet-WordNet Semantic Graph Example.

This example demonstrates the integration of VerbNet, FrameNet, and WordNet corpora
through their semantic mappings and cross-references. It shows how verb classes from
VerbNet connect to semantic frames in FrameNet and word senses in WordNet.

This example demonstrates how to:
1. Load VerbNet, FrameNet, and WordNet data using UVI
2. Create an integrated semantic graph linking the three corpora
3. Visualize cross-corpus mappings and relationships
4. Explore semantic connections between verb classes, frames, and synsets

Usage:
    python vn_fn_wn_graph.py

Features:
- Interactive visualization with corpus-specific node shapes and colors
- Hover over nodes to see detailed corpus information
- Click nodes to select and highlight connected semantic networks
- Cross-corpus connection visualization with different edge styles
- Save functionality to export the integrated graph
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi import UVI
from uvi.graph.VerbNetFrameNetWordNetGraphBuilder import VerbNetFrameNetWordNetGraphBuilder
from uvi.visualizations.VerbNetFrameNetWordNetVisualizer import VerbNetFrameNetWordNetVisualizer

# Import required packages
try:
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Please install required packages: pip install networkx matplotlib")
    print(f"Error: {e}")
    sys.exit(1)


def main():
    """Main function for integrated VerbNet-FrameNet-WordNet visualization."""
    print("=" * 60)
    print("Integrated VerbNet-FrameNet-WordNet Semantic Graph Demo")
    print("=" * 60)
    
    # Initialize UVI and load all three corpora
    corpora_path = Path(__file__).parent.parent / 'corpora'
    print(f"Loading corpora from: {corpora_path}")
    
    try:
        uvi = UVI(str(corpora_path), load_all=False)
        
        # Load the three corpora
        print("Loading VerbNet...")
        uvi._load_corpus('verbnet')
        
        print("Loading FrameNet...")
        uvi._load_corpus('framenet')
        
        print("Loading WordNet...")
        uvi._load_corpus('wordnet')
        
        # Check that all corpora loaded successfully
        corpus_info = uvi.get_corpus_info()
        required_corpora = ['verbnet', 'framenet', 'wordnet']
        missing_corpora = []
        
        for corpus in required_corpora:
            if not corpus_info.get(corpus, {}).get('loaded', False):
                missing_corpora.append(corpus)
        
        if missing_corpora:
            print(f"ERROR: The following corpora failed to load: {', '.join(missing_corpora)}")
            print("Make sure all corpus data is available in the corpora directory")
            return
        
        print("All corpora loaded successfully!")
        
        # Get corpus data
        verbnet_data = uvi.corpora_data['verbnet']
        framenet_data = uvi.corpora_data['framenet']
        wordnet_data = uvi.corpora_data['wordnet']
        
        # Display corpus statistics
        vn_classes = len(verbnet_data.get('classes', {}))
        fn_frames = len(framenet_data.get('frames', {}))
        wn_synsets = sum(len(s) for s in wordnet_data.get('synsets', {}).values())
        
        print(f"\nCorpus Statistics:")
        print(f"  VerbNet classes: {vn_classes}")
        print(f"  FrameNet frames: {fn_frames}")
        print(f"  WordNet synsets: {wn_synsets}")
        
        # Create integrated semantic graph
        print(f"\nCreating integrated semantic graph...")
        graph_builder = VerbNetFrameNetWordNetGraphBuilder()
        
        G, hierarchy = graph_builder.create_integrated_graph(
            verbnet_data=verbnet_data,
            framenet_data=framenet_data,
            wordnet_data=wordnet_data,
            num_vn_classes=6,              # Number of VerbNet classes to include
            max_fn_frames_per_class=2,     # Max FrameNet frames per VerbNet class
            max_wn_synsets_per_class=2,    # Max WordNet synsets per VerbNet class
            include_members=True,          # Include member verbs
            max_members_per_class=3        # Max member verbs per class
        )
        
        if G is None or G.number_of_nodes() == 0:
            print("Could not create integrated visualization graph")
            return
        
        print(f"\nCreated integrated graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        # Create interactive visualization
        print(f"\nLaunching interactive visualization...")
        print("\nVisualization Features:")
        print("- Blue squares (□): VerbNet verb classes")
        print("- Purple triangles (△): FrameNet semantic frames")  
        print("- Green diamonds (◇): WordNet synsets")
        print("- Orange circles (○): Member verbs")
        print("- Different edge styles show cross-corpus connections")
        print("\nInteraction Instructions:")
        print("- Hover over nodes to see detailed corpus information")
        print("- Click on nodes to select and highlight semantic networks")
        print("- Use toolbar to zoom and pan around the graph")
        print("- Click 'Save PNG' to export current view")
        print("- Close window when finished exploring")
        
        # Create specialized integrated visualizer
        visualizer = VerbNetFrameNetWordNetVisualizer(
            G, hierarchy, "Integrated VerbNet-FrameNet-WordNet Semantic Graph"
        )
        
        fig = visualizer.create_interactive_plot()
        plt.show()
        
        print("\n" + "=" * 60)
        print("Integrated semantic graph demo complete!")
        print("\nThis demo showed how VerbNet verb classes connect to:")
        print("- FrameNet semantic frames through shared conceptual structures")
        print("- WordNet synsets through lexical semantic mappings")
        print("- Member verbs that bridge all three linguistic resources")
        print("- Cross-corpus semantic networks for comprehensive verb analysis")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure VerbNet, FrameNet, and WordNet data are available in the corpora directory")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()