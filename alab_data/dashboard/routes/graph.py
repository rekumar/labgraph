from typing import List
from bson import ObjectId
from flask import Blueprint, request
from pydantic import ValidationError
from alab_data.views import (
    SampleView,
    MeasurementView,
    MaterialView,
    ActionView,
    AnalysisView,
)
import pymongo
from dataclasses import dataclass, asdict
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from .utils import MongoEncoder
import json

sample_view: SampleView = SampleView()
node_views = {
    "measurement": MeasurementView(),
    "material": MaterialView(),
    "action": ActionView(),
    "analysis": AnalysisView(),
}

### Dataclasses
@dataclass
class NodeEntry:
    _id: str
    x: float
    y: float
    label: str
    size: float
    contents: dict


@dataclass
class EdgeEntry:
    source: str
    target: str
    contents: dict


@dataclass
class Graph:
    nodes: List[NodeEntry]
    edges: List[EdgeEntry]


### API
graph_bp = Blueprint("/graph", __name__, url_prefix="/api/graph")


@graph_bp.route("/complete", methods=["GET"])
def get_complete_graph() -> Graph:
    """
    Get the summary of all samples
    """

    g = nx.DiGraph()

    for node_type, view in node_views.items():
        for node in view._collection.find():
            upstream = node.pop("upstream")
            downstream = node.pop("downstream")
            g.add_node(node["_id"], type=node_type, **node)
            for u in upstream:
                g.add_edge(u["node_id"], node["_id"])
            for d in downstream:
                g.add_edge(node["_id"], d["node_id"])

    layout = graphviz_layout(g, prog="dot")

    nodes = []
    edges = []

    for node_id, node in g.nodes(data=True):
        nodes.append(
            NodeEntry(
                _id=str(node_id),
                x=layout[node_id][0],
                y=layout[node_id][1],
                label=node["name"],
                size=10,
                contents=node,
            )
        )
    for source, target, data in g.edges(data=True):
        edges.append(
            EdgeEntry(
                source=str(source),
                target=str(target),
                contents=data,
            )
        )
    gdict = asdict(Graph(nodes, edges))
    return json.loads(MongoEncoder().encode(gdict))
