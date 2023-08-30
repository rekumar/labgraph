from typing import Any, List, Union
import networkx as nx
from bson import ObjectId
import matplotlib.pyplot as plt
import itertools as itt

from labgraph.utils.graph import hierarchical_layout
from labgraph.utils.plot import plot_graph
from .nodes import (
    BaseNode,
    Material,
    Action,
    Measurement,
    Analysis,
    WholeIngredient,
)
from datetime import datetime

ALLOWED_NODE_TYPE = Union[Material, Action, Measurement, Analysis]


class Sample:
    def __init__(
        self,
        name: str,
        description: str = None,
        nodes: List[ALLOWED_NODE_TYPE] = None,
        tags: List[str] = None,
        **contents,
    ):
        self.name = name
        self.description = description
        self._id = ObjectId()
        self._contents = contents
        self._created_at = None
        self._updated_at = None

        self.description = description or ""
        self.tags = tags or []
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
        if node in self.nodes:
            return  # we already have this node. Do we need to update it? TODO
        self.nodes.append(node)

    def add_linear_process(self, actions: List[Action]):
        """
        Add a linear process to the sample. A "linear process" is a series of Actions where the total output Material from each Action is fed into the follwing Action.

        Essentially, this is a helper function to stitch basic processes into a valid graph
        """
        ## Make sure a linear process is appropriate for the given sequence of Actions
        for a in actions[:-1]:
            if len(a.generated_materials) not in [0, 1]:
                raise ValueError(
                    "All Actions of a linear process (except the final Action) must generate exactly one material!"
                )

        for action0, action1 in zip(actions, actions[1:]):
            if len(action1.ingredients) == 0:
                continue  # ingredients will be automatically set to the output material of action0
            if not any(
                [
                    ingredient.material in action0.generated_materials
                    for ingredient in action1.ingredients
                ]
            ):
                raise ValueError(
                    f"No ingredients for {action1} were generated by {action0}. In a linear process, each Action must use Material(s) generated by the preceding Action. If ingredients are already specified for an Action, at least one must be generated by the preceding Action."
                )

        # add the initial action + ingredient materials
        for ingredient in actions[0].ingredients:
            self.add_node(ingredient.material)
        self.add_node(actions[0])

        # add the intervening actions and implicit intermediate materials
        for action0, action1 in zip(actions, actions[1:]):
            if len(action0.generated_materials) == 0:
                intermediate_material = action0.make_generic_generated_material()
            elif len(action0.generated_materials) == 1:
                intermediate_material = action0.generated_materials[0]
            self.add_node(intermediate_material)
            if len(action1.ingredients) == 0:
                action1.add_ingredient(WholeIngredient(intermediate_material))
            # action1.add_ingredient(WholeIngredient(material=intermediate_material))
            self.add_node(action1)

        # add the final material
        if len(actions[-1].generated_materials) == 0:
            actions[-1].make_generic_generated_material()
        for final_material in actions[-1].generated_materials:
            self.add_node(final_material)

    @property
    def graph(self):
        graph = nx.DiGraph()
        for node in self.nodes:
            node: BaseNode
            graph.add_node(node.id, type=node.labgraph_node_type, name=node.name)
            for upstream in node.upstream:
                if upstream["node_id"] not in graph.nodes:
                    graph.add_node(
                        upstream["node_id"], type=upstream["node_type"], name=""
                    )  # TODO how should we name nodes that are outside of the sample scope? Currently just empty name
                graph.add_edge(upstream["node_id"], node.id)
            for downstream in node.downstream:
                if downstream["node_id"] not in graph.nodes:
                    graph.add_node(
                        downstream["node_id"], type=downstream["node_type"], name=""
                    )
                graph.add_edge(node.id, downstream["node_id"])
        return graph

    @property
    def has_valid_graph(self) -> bool:
        is_acyclic = nx.is_directed_acyclic_graph(self.graph)
        num_connected_components = len(
            list(nx.connected_components(self.graph.to_undirected()))
        )
        return is_acyclic and (num_connected_components == 1)

    def get_action_graph(self, include_outside_nodes: bool = False) -> nx.DiGraph:
        """
        Return a reduced version of the Sample graph that only contains Actions. useful for comparing the process involved in making two Samples

        Args:
            include_outside_nodes (bool, optional): If True, include nodes that are not part of the Sample (ie Actions that are immediately upstream of the first Action within this Sample) in the returned graph. Defaults to False.
        """
        g = self.graph

        nodes_to_delete = [
            nid for nid, ndata in g.nodes(data=True) if ndata["type"] != "Action"
        ]

        for node in nodes_to_delete:
            g.add_edges_from(itt.product(g.predecessors(node), g.successors(node)))
            g.remove_node(node)

        if not include_outside_nodes:
            nodes_to_delete = []
            for nid in g.nodes:
                if not any([nid == node.id for node in self.nodes]):
                    nodes_to_delete.append(nid)
            for nid in nodes_to_delete:
                g.remove_node(nid)
        return g

    def to_dict(self, verbose: bool = False) -> dict:
        node_dict = {
            nodetype: []
            for nodetype in ["Material", "Action", "Analysis", "Measurement"]
        }
        for node in self.nodes:
            node: BaseNode
            node_dict[node.labgraph_node_type].append(node.id)

        entry = {
            "_id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": node_dict,
            "tags": self.tags,
        }

        # for parameter_name in self._contents:
        #     if parameter_name in entry:
        #         raise ValueError(
        #             f"User field name {parameter_name} is not allowed, as it collides with a default key in a Sample entry! Please change this name and try again."
        #         )
        # entry.update(self._contents)
        # entry.pop("version_history", None)

        entry["contents"] = self._contents
        if verbose:
            self._sort_nodes()
            entry["node_contents"] = [node.to_dict() for node in self.nodes]

        return entry

    def plot(self, with_labels: bool = True, ax: plt.Axes = None):
        """Plots the sample graph. This is pretty chaotic with branched graphs, but can give a qualitative sense of the experimental procedure

        Args:
            with_labels (bool, optional): Whether to show the node names. Defaults to True.
            ax (matplotlib.pyplot.Axes, optional): Existing plot Axes to draw the graph onto. If None, a new plot figure+axes will be created. Defaults to None.
        """
        plot_graph(graph=self.graph, with_labels=with_labels, ax=ax)

    def _sort_nodes(self):
        """
        sort the node list in graph hierarchical order
        """
        weights = list(nx.topological_sort(self.graph))
        self.nodes.sort(key=lambda node: weights.index(node.id))

    def __repr__(self):
        return f"<Sample: {self.name}>"

    def __eq__(self, other):
        if not isinstance(other, Sample):
            return False
        return other.id == self.id

    def __getitem__(self, key: str):
        return self._contents[key]

    def __setitem__(self, key: str, value: Any):
        self._contents[key] = value

    def keys(self):
        return list(self._contents.keys())

    def save(self):
        """Save or update the sample in the database"""
        from labgraph.views import SampleView

        SampleView().add(entry=self, if_already_in_db="update")

    @classmethod
    def get(self, id: ObjectId) -> "Sample":
        """Get a sample from the database by id

        Args:
            id (str): id of the sample

        Returns:
            Sample: Sample object
        """
        from labgraph.views import SampleView

        return SampleView().get(id)

    @classmethod
    def get_by_name(self, name: str) -> List["Sample"]:
        """Get a sample from the database by name

        Args:
            name (str): name of the sample. Note that sample names are not unique, so multiple samples may be returned.

        Returns:
            List[Sample]: List of Sample objects with the given name
        """
        from labgraph.views import SampleView

        return SampleView().get_by_name(name)

    @classmethod
    def get_by_tags(self, tags: List[str]) -> List["Sample"]:
        """Get a sample from the database by tags

        Args:
            tags (List[str]): tags of the sample. Only samples with all of the given tags will be returned.

        Returns:
            List[Sample]: List of Sample objects with the given tags.
        """
        from labgraph.views import SampleView

        return SampleView().get_by_tags(tags)

    @classmethod
    def get_by_contents(self, contents: dict) -> List["Sample"]:
        """Return all Sample(s) that contain the given key-value pairs in their document.

        Args:
            contents (dict): Dictionary of contents to match against. Samples which contain all of the provided key-value pairs will be returned.

        Raises:
            NotFoundInDatabaseError: No Sample found with specified contents

        Returns:
            List[Sample]: List of Sample(s) with the specified contents. List is sorted from most recent to oldest.
        """
        from labgraph.views import SampleView

        return SampleView().get_by_contents(contents)

    @classmethod
    def filter(
        self,
        filter_dict: dict,
        datetime_min: datetime = None,
        datetime_max: datetime = None,
    ) -> List["Sample"]:
        """Thin wrapper around pymongo find method, with an extra datetime filter.

        Args:
            filter_dict (Dict): standard mongodb filter dictionary.
            datetime_min (datetime, optional): entries from before this datetime will not be shown. Defaults to None.
            datetime_max (datetime, optional): entries from after this datetime will not be shown. Defaults to None.

        Returns:
            List[BaseObject]: List of Samples that match the filter
        """
        from labgraph.views import SampleView

        return SampleView().filter(filter_dict, datetime_min, datetime_max)

    @classmethod
    def filter_one(
        self,
        filter_dict: dict,
        datetime_min: datetime = None,
        datetime_max: datetime = None,
    ) -> "Sample":
        """Thin wrapper around pymongo find_one method, with an extra datetime filter.

        Args:
            filter_dict (Dict): standard mongodb filter dictionary.
            datetime_min (datetime, optional): entries from before this datetime will not be shown. Defaults to None.
            datetime_max (datetime, optional): entries from after this datetime will not be shown. Defaults to None.

        Returns:
            BaseObject: Sample that matches the filter
        """
        from labgraph.views import SampleView

        return SampleView().filter_one(filter_dict, datetime_min, datetime_max)

    @classmethod
    def get_by_node(self, node: Union[BaseNode, List[BaseNode]]) -> List["Sample"]:
        """Get Sample(s) from the database by node

        Args:
            node (BaseNode): A Node object (Action, Analysis, Measurement, or Material).

        Returns:
            List[Sample]: List of Sample objects which contain the given node.
        """
        from labgraph.views import SampleView

        if isinstance(node, BaseNode):
            return SampleView().get_by_node(node)
        elif isinstance(node, list):
            results = []
            for n in node:
                results.extend(SampleView().get_by_node(n))
            return list(set(results))

    def __hash__(self):
        return hash(self.id)

    @property
    def created_at(self):
        if self._created_at is None:
            return f"{self} has not been saved to the database yet."
        return self._created_at

    @property
    def updated_at(self):
        if self._updated_at is None:
            return f"{self} has not been saved to the database yet."
        return self._updated_at


def action_sequence_distance(
    s1: Sample, s2: Sample, include_outside_nodes: float = False
) -> float:
    """
    Compute the distance between action sequences of two samples. This is the graph edit distance between subgraphs of each sample, where each subgraph is reduced to contain only Actions. Actions are considered equivalent if they have the same name.

    Args:
        s1 (Sample): Sample 1
        s2 (Sample): Sample 2
        include_outside_nodes (bool, optional): If True, include nodes that are not part of the Sample (ie Actions that are immediately upstream of the first Action within this Sample) in the returned graph. Defaults to False.

    Returns:
        float: distance between the two samples Action sequences. 0 means identical.
    """

    def node_match(n1, n2):
        return (n1["type"] == n2["type"]) and (n1["name"] == n2["name"])

    g1 = s1.get_action_graph(include_outside_nodes=include_outside_nodes)
    g2 = s2.get_action_graph(include_outside_nodes=include_outside_nodes)
    return nx.graph_edit_distance(g1, g2, node_match=node_match)
