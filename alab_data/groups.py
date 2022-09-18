from typing import List, Union
import networkx as nx
from bson import ObjectId

from alab_data.units.nodes import (
    Material,
    Action,
    Measurement,
    Analysis,
)

ALLOWED_NODE_TYPE = Union[Material, Action, Measurement, Analysis]


class Sample:
    def __init__(
        self,
        name: str,
        description: str = "",
        nodes: List[ALLOWED_NODE_TYPE] = None,
        tags: List[str] = None,
    ):
        self.name = name
        self.description = description
        self.graph = nx.DiGraph()
        self._id = ObjectId()

        if tags is None:
            self.tags = []
        else:
            self.tags = tags
        self.nodes = []
        if nodes is not None:
            for node in nodes:
                # do it this way to type check each node before adding it to this Sample
                self.add_node(node)

    @property
    def id(self):
        return self._id

    def add_node(self, node: ALLOWED_NODE_TYPE):
        if not any(
            [isinstance(node, x) for x in [Material, Action, Analysis, Measurement]]
        ):
            raise ValueError(
                "Node must be a Material, Action, Analysis, or Measurement object!"
            )
        self.graph.add_node(node.id)
        for upstream in node.upstream:
            self.graph.add_edge(upstream, node.id)
        for downstream in node.downstream:
            self.graph.add_edge(node.id, downstream)
        self.nodes.append(node)

    def has_valid_graph(self):
        return nx.is_directed_acyclic_graph(self.graph) and (
            len(list(nx.isolates(self.graph))) == 0
        )

    def to_dict(self):
        node_dict = {
            nodetype.__name__: [] for nodetype in [Material, Action, Analysis, Measurement]
        }
        for node in self.nodes:
            node_dict[type(node).__name__].append(node.id)

        return {
            "_id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": node_dict,
            "tags": self.tags,
        }

    # def add_to_db(self):
    #     from alab_data.views import (
    #         ActionView,
    #         MaterialView,
    #         AnalysisView,
    #         MeasurementView,
    #     )

    #     for node in self.nodes:
    #         if isinstance(node, Material):
    #             MaterialView().add(node)
    #         elif isinstance(node, Action):
    #             ActionView().add(node)
    #         elif isinstance(node, Analysis):
    #             AnalysisView().add(node)
    #         elif isinstance(node, Measurement):
    #             MeasurementView().add(node)

    def __repr__(self):
        return f"Sample({self.name})"
