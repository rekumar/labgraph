from typing import List, Union
import networkx as nx
from bson import ObjectId
import matplotlib.pyplot as plt

from .nodes import (
    Material,
    Action,
    Measurement,
    Analysis,
    WholeIngredient,
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
        self.graph.add_node(node.id, type=type(node), name=node.name)
        for upstream in node.upstream:
            self.graph.add_edge(upstream, node.id)
        for downstream in node.downstream:
            self.graph.add_edge(node.id, downstream)
        self.nodes.append(node)

    def add_linear_process(self, actions: List[Action]):
        """
        Add a linear process to the sample. A "linear process" is a series of Actions where the total output Material from each Action is fed into the follwing Action.

        Essentially, this is a helper function to stitch basic processes into a valid graph
        """
        # create the first material
        for a in actions[:-1]:
            if len(a.generated_materials) not in [0, 1]:
                raise ValueError(
                    "All Actions of a linear process (except the final Action) must generate exactly one material!"
                )
        # add the initial action + ingredient materials
        self.add_node(actions[0])
        for ingredient in actions[0].ingredients:
            self.add_node(ingredient.material)

        # add the intervening actions and implicit intermediate materials
        for action0, action1 in zip(actions, actions[1:]):
            if len(action0.generated_materials) == 0:
                intermediate_material = action0.make_generic_generated_material()
            elif len(action0.generated_materials) == 1:
                intermediate_material = action0.generated_materials[0]
            self.add_node(intermediate_material)
            action1.add_ingredient(WholeIngredient(material=intermediate_material))
            self.add_node(action1)

        # add the final material
        if len(actions[-1].generated_materials) == 0:
            actions[-1].make_generic_generated_material()
        for final_material in actions[-1].generated_materials:
            self.add_node(final_material)

    def has_valid_graph(self) -> bool:
        return nx.is_directed_acyclic_graph(self.graph) and (
            len(list(nx.isolates(self.graph))) == 0
        )

    def to_dict(self) -> dict:
        node_dict = {
            nodetype.__name__: []
            for nodetype in [Material, Action, Analysis, Measurement]
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

    def plot(self, with_labels: bool = True, ax: plt.Axes = None):
        """Plots the sample graph. This is pretty chaotic with branched graphs, but can give a qualitative sense of the experimental procedure

        Args:
            with_labels (bool, optional): Whether to show the node names. Defaults to True.
            ax (matplotlib.pyplot.Axes, optional): Existing plot Axes to draw the graph onto. If None, a new plot figure+axes will be created. Defaults to None.
        """
        if ax is None:
            fig, ax = plt.subplots()

        color_key = {
            nodetype: plt.cm.tab10(i)
            for i, nodetype in enumerate([Material, Action, Analysis, Measurement])
        }
        node_colors = []
        node_labels = {}
        for node in self.graph.nodes:
            node_labels[node] = self.graph.nodes[node]["name"]
            node_colors.append(color_key[self.graph.nodes[node]["type"]])
        nx.draw(
            self.graph,
            with_labels=with_labels,
            node_color=node_colors,
            labels=node_labels,
            ax=ax,
        )

    def __repr__(self):
        return f"Sample({self.name})"
