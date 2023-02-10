from typing import Dict, List, Optional, TYPE_CHECKING

from bson import ObjectId
from labgraph.data.nodes import BaseNode, NodeList
from labgraph import views

if TYPE_CHECKING:
    from labgraph.data.sample import Sample


def _get_affected_nodes(
    node: BaseNode, affected_nodes: Optional[Dict[str, List[str]]] = None
):
    """Recursively gets node ids that would be affected by a change to a given node. This assumes that all nodes downstream of a given node are dependent on it!"""
    VIEWS = {
        "Action": views.ActionView,
        "Analysis": views.AnalysisView,
        "Measurement": views.MeasurementView,
        "Material": views.MaterialView,
    }

    affected_nodes = affected_nodes or {
        "Action": [],
        "Analysis": [],
        "Measurement": [],
        "Material": [],
    }
    for i, downstream in enumerate(node.downstream):
        type_list = affected_nodes[downstream["node_type"]]
        if downstream["node_id"] in type_list:
            continue
        type_list.append(downstream["node_id"])
        affected_nodes = _get_affected_nodes(node.downstream.get(i), affected_nodes)

    return affected_nodes


def get_affected_nodes(node: BaseNode) -> NodeList:
    """Get all nodes affected by a change to a given node. This assumes that all nodes downstream of a given node are dependent on it!

    Args:
        node (Node): Node to check

    Returns:
        list: List of affected nodes
    """
    affected_by_type = _get_affected_nodes(node)
    affected_nodes = NodeList()
    for node_type, node_ids in affected_by_type.items():
        for node_id in node_ids:
            affected_nodes.append(
                {
                    "node_type": node_type,
                    "node_id": node_id,
                }
            )
    return affected_nodes


def get_affected_samples(node: BaseNode) -> List["Sample"]:
    """Get all samples affected by a change to a given node. This assumes that all nodes downstream of a given node are dependent on it!

    Args:
        node (Node): Node to check

    Returns:
        list: List of affected samples
    """
    sampleview = views.SampleView()
    affected_nodes = get_affected_nodes(node)
    affected_nodes.append(node)  # this node matters too!
    affected_samples = []
    for node in affected_nodes.get():
        for sample in sampleview.get_by_node(node):
            if sample not in affected_samples:
                affected_samples.append(sample)

    return affected_samples


def _remove_references_to_node(node_type: str, node_id: ObjectId):
    """Removes all edges and sample references that point to the given node.
        This is used internally by node/sample deletion routines. Not intended for users, be careful with this -- it can render graphs invalid!

    Args:
        node_type (str): Type of node to be removed (Action, Analysis, Measurement, Material)
        node_id (ObjectId): ID of node to be removed
    """
    from labgraph.views import (
        ActionView,
        AnalysisView,
        MeasurementView,
        MaterialView,
        SampleView,
    )

    for view in [ActionView(), AnalysisView(), MeasurementView(), MaterialView()]:
        view._collection.update_many(
            {"downstream": {"node_type": node_type, "node_id": node_id}},
            {"$pull": {"downstream": {"node_type": node_type, "node_id": node_id}}},
        )
        view._collection.update_many(
            {"upstream": {"node_type": node_type, "node_id": node_id}},
            {"$pull": {"upstream": {"node_type": node_type, "node_id": node_id}}},
        )

    SampleView()._collection.update_many(
        {f"nodes.{node_type}": node_id},
        {"$pull": {f"nodes.{node_type}": node_id}},
    )
