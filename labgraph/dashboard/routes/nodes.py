from typing import Literal
from bson import ObjectId
from flask import Blueprint
from labgraph.views import MeasurementView, MaterialView, ActionView, AnalysisView
from labgraph.views.base import BaseView


node_views = {
    "measurement": MeasurementView(),
    "material": MaterialView(),
    "action": ActionView(),
    "analysis": AnalysisView(),
}


measurement_bp = Blueprint("/measurement", __name__, url_prefix="/api/measurement")
material_bp = Blueprint("/material", __name__, url_prefix="/api/material")
action_bp = Blueprint("/action", __name__, url_prefix="/api/action")
analysis_bp = Blueprint("/analysis", __name__, url_prefix="/api/analysis")


def get_node(
    node_type: Literal["measurement", "material", "analysis", "action"], node_id: str
):
    """
    Get the status of a node
    """
    try:
        if node_type not in node_views:
            raise ValueError(f"Invalid node type {node_type}")
        view: BaseView = node_views[node_type]
        node_entry = view._collection.find_one(
            {"_id": ObjectId(node_id)},
        )
        if node_entry is None:
            raise ValueError(f"No {node_type} node found with id {node_id}")
    except ValueError as exception:
        return {"status": "error", "errors": exception.args[0]}, 400

    node_entry["_id"] = str(node_entry["_id"])
    node_entry["upstream"] = [
        {
            "node_type": i["node_type"],
            "node_id": str(i["node_id"]),
        }
        for i in node_entry["upstream"]
    ]
    node_entry["downstream"] = [
        {
            "node_type": i["node_type"],
            "node_id": str(i["node_id"]),
        }
        for i in node_entry["downstream"]
    ]

    return node_entry


@measurement_bp.route("/<measurement_id>", methods=["GET"])
def get_measurement(measurement_id):
    return get_node("measurement", measurement_id)


@material_bp.route("/<material_id>", methods=["GET"])
def get_material(material_id):
    return get_node("material", material_id)


@action_bp.route("/<action_id>", methods=["GET"])
def get_action(action_id):
    return get_node("action", action_id)


@analysis_bp.route("/<analysis_id>", methods=["GET"])
def get_analysis(analysis_id):
    return get_node("analysis", analysis_id)
