from typing import List, TYPE_CHECKING
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import warnings

if TYPE_CHECKING:
    from labgraph.data.sample import Sample


def plot_multiple_samples(samples: List["Sample"], ax: plt.axes = None):
    graph = nx.DiGraph()
    for sample in samples:
        graph = nx.compose(graph, sample.graph)
    plot_graph(graph, ax=ax)


def plot_graph(graph: nx.DiGraph, with_labels: bool = True, ax: plt.axes = None):
    """Plots the sample graph. This is pretty chaotic with branched graphs, but can give a qualitative sense of the experimental procedure

    Args:
        with_labels (bool, optional): Whether to show the node names. Defaults to True.
        ax (matplotlib.pyplot.Axes, optional): Existing plot Axes to draw the graph onto. If None, a new plot figure+axes will be created. Defaults to None.
    """
    if ax is None:
        fig, ax = plt.subplots()

    color_key = {
        nodetype: plt.cm.tab10(i)
        for i, nodetype in enumerate(["Material", "Action", "Analysis", "Measurement"])
    }
    node_colors = []
    node_labels = {}
    for node in graph.nodes:
        node_labels[node] = graph.nodes[node]["name"]
        color = color_key[graph.nodes[node]["type"]]
        if node_labels[node] == "":
            color = tuple(
                [*color[:3], 0.4]
            )  # low opacity for attached nodes that are not part of the sample
        node_colors.append(color)
    try:
        layout = graphviz_layout(graph, prog="dot")
    except:
        warnings.warn(
            "Could not use graphviz layout, falling back to default networkx layout. Ensure that graphviz and pygraphviz are installed to enable hierarchical graph layouts. This only affects graph visualization."
        )
        layout = nx.spring_layout(graph)
        # layout = hierarchical_layout(self.graph) #TODO substitute graphviz to remove dependency.
    nx.draw(
        graph,
        with_labels=with_labels,
        node_color=node_colors,
        labels=node_labels,
        pos=layout,
        ax=ax,
    )
