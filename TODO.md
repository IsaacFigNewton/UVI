# Visualization bugs
## Fixes to implement across all visualizers
- remove the custom "Save PNG" buttons
- reduce the plotly figures' dimensions (shrink the figure's display window)
- ensure nodes do not overlap
- plotly "Reset original view" button fails to revert the original figure

## FrameNetVisualizer
- instructions rendered incorrectly
 - use VerbNetFrameNetWordNetVisualizer implementation
- combine the following node types into a single 'Frame' type
```python
    Patch(facecolor='lightblue', label='Source Frames (no parents)'),
    Patch(facecolor='lightgreen', label='Intermediate Frames'),
    Patch(facecolor='lightcoral', label='Sink Frames (no children)'),
    Patch(facecolor='lightgray', label='Isolated Frames'),
```
- when a node is selected, as in VerbNetFrameNetWordNetVisualizer, all non-neighboring nodes should be turned grey
 - fix by using VerbNetFrameNetWordNetVisualizer implementation

## VerbNetVisualizer
- instructions rendered incorrectly
 - use VerbNetFrameNetWordNetVisualizer implementation
- remove the "Selected Node" legend entries
- when a node is selected, as in VerbNetFrameNetWordNetVisualizer, all non-neighboring nodes should be turned grey
 - fix by using VerbNetFrameNetWordNetVisualizer implementation

## WordNetVisualizer
- instructions rendered incorrectly
 - use VerbNetFrameNetWordNetVisualizer implementation
- remove the "Selected Node" legend entries
- when a node is selected, as in VerbNetFrameNetWordNetVisualizer, all non-neighboring nodes should be turned grey
 - fix by using VerbNetFrameNetWordNetVisualizer implementation
- node labels should include the full wordnet synset name, not just the synset's primary lemma
 - e.g. "substance" ==> "substance.n.01"

## VerbNetFrameNetWordNetVisualizer
- instructions rendered correctly
- color-coded corpus names in the legend overflow onto the node type texts, e.g. a blue "VerbNet" label overlaps with the black node type text "VerbNet Classes"
 - just remove these colored corpus names and leave the color swatch - node type text pairings
- title text is cut off by the figure's boundaries, as it extends upwards, out of the figure frame
- title text replaced with node metadata when hovering over a node. this is incorrect; plotly should display a tooltip with information, just as implemented in VerbNetVisualizer
- all unselected nodes lose their shapes when a single node is clicked
 - shapes should be preserved
 - correctly turns non-neighboring nodes grey
- node labels should include the full wordnet synset name, not just the synset's primary lemma
 - e.g. "substance" ==> "substance.n.01"