import networkx as nx
from typing import List, Dict, Tuple


def get_subgraphs(graph: nx.DiGraph) -> List[nx.DiGraph]:
    """Return subgraphs of a DiGraph. A subgraph is a set of connected nodes that are not connected to any other nodes in the graph.

    Args:
        graph (nx.DiGraph): directed graph of an experiment

    Returns:
        List[nx.Digraph]: list of subgraphs of the directed graph.
    """
    subgraphs = [
        graph.subgraph(c) for c in nx.connected_components(graph.to_undirected())
    ]
    return subgraphs


def _walk_graph_for_positions(graph, positions=None, node=None, x0=0, y0=0, width=1):
    if node is None:
        node = list(nx.topological_sort(graph))[0]
    if positions is None:
        positions = {}
    positions[node] = (x0, y0)

    successors = list(graph.successors(node))
    if len(successors) == 0:
        return

    if len(successors) == 1:
        dx = width
        x = [0]
    else:
        dx = width / (len(successors) - 1)
        x = [i * dx - width / 2 for i in range(len(successors))]

    for delta_x, successor in zip(x, successors):
        next_successors = list(graph.successors(successor))
        if len(next_successors) != 0:
            width = dx * (len(next_successors) - 1) / len(next_successors) * 0.95
        _walk_graph_for_positions(
            graph, positions, successor, x0=x0 + delta_x, y0=y0 - 1, width=width
        )

    return positions


def hierarchical_layout(graph: nx.DiGraph) -> Dict[str, Tuple[float, float]]:
    """Create a hierarchical layout for a directed graph

    Args:s
        graph (nx.DiGraph): graph to layout

    Returns:
        dict: mapping of node ids to (x,y) coordinates
    """
    subgraphs = get_subgraphs(graph)
    subgraph_positions = []
    subgraph_bounds = []
    for subgraph in get_subgraphs(graph):
        subgraph_positions.append(_walk_graph_for_positions(subgraph))

        max_x = max([x for x, y in subgraph_positions[-1].values()])
        min_x = min([x for x, y in subgraph_positions[-1].values()])
        subgraph_bounds.append((min_x, max_x))

    positions = {}
    reference_x = 0
    total_width = sum([max_x - min_x for min_x, max_x in subgraph_bounds])
    TARGET_MARGIN = total_width * 0.05
    for subgraph, (min_x, max_x) in zip(subgraphs, subgraph_bounds):
        overlap = reference_x - min_x
        offset = TARGET_MARGIN + overlap
        for node, (x, y) in subgraph_positions.pop(0).items():
            positions[node] = (x + offset, y)
        reference_x = max_x + offset

    return positions

