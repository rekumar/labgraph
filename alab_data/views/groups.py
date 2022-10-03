from datetime import datetime
from typing import Dict, List, cast
from alab_data.data import Action, Analysis, Material, Measurement, Sample
from alab_data.utils.data_objects import get_collection
from alab_data.views.nodes import (
    ActionView,
    MaterialView,
    AnalysisView,
    MeasurementView,
)
from .base import BaseView, NotFoundInDatabaseError
from bson import ObjectId


class SampleView(BaseView):
    def __init__(self):
        super().__init__("samples", Sample)
        self._collection = get_collection("samples")
        self.actionview = ActionView()
        self.materialview = MaterialView()
        self.analysisview = AnalysisView()
        self.measurementview = MeasurementView()

    def add(self, entry: Sample) -> ObjectId:
        if not isinstance(entry, self._entry_class):
            raise ValueError(f"Entry must be of type {self._entry_class.__name__}")

        if not entry.has_valid_graph():
            raise ValueError(
                "Sample graph is not valid! Check for isolated nodes or graph cycles."
            )

        found_in_db = False
        try:
            self.get(id=entry.id)
            found_in_db = True
        except ValueError:
            pass
        if found_in_db:
            raise ValueError(
                f"{self._entry_class.__name__} (name={entry.name}, id={entry.id}) already exists in the database!"
            )

        # TODO check all nodes before uploading so we dont put half the nodes in before hitting a snag.
        if not self._has_valid_graph_in_db(entry):
            raise ValueError(
                "Sample graph is not valid! Check for isolated nodes or graph cycles."
            )
        for node in entry.nodes:
            if isinstance(node, Action):
                self.actionview.add(node, pass_if_already_in_db=True)
            elif isinstance(node, Material):
                self.materialview.add(node, pass_if_already_in_db=True)
            elif isinstance(node, Analysis):
                self.analysisview.add(node, pass_if_already_in_db=True)
            elif isinstance(node, Measurement):
                self.measurementview.add(node, pass_if_already_in_db=True)
            else:
                raise ValueError(f"Node {node} is not a valid node type")

        result = self._collection.insert_one(
            {
                **entry.to_dict(),
                "created_at": datetime.now(),
            }
        )
        return cast(ObjectId, result.inserted_id)

    def _has_valid_graph_in_db(self, sample: Sample) -> bool:
        # we need to check the graph in the db to make sure it is valid.

        upcoming_nodes = [
            node.id for node in sample.nodes
        ]  # all nodes that will be added along with this sample

        # checkifvalid_methods = {
        #     Action: self._is_valid_action,
        #     Material: self._is_valid_material,
        #     Measurement: self._is_valid_measurement,
        #     Analysis: self._is_valid_analysis,
        # }

        checkifvalid_methods = {
            "Action": self.actionview.get,
            "Material": self.materialview.get,
            "Measurement": self.measurementview.get,
            "Analysis": self.analysisview.get,
        }

        for node in sample.nodes:
            for related_node in node.upstream + node.downstream:
                if related_node["node_id"] in upcoming_nodes:
                    continue
                try:
                    checkifvalid = checkifvalid_methods[related_node["node_type"]]
                    checkifvalid(id=related_node["node_id"])
                except NotFoundInDatabaseError as e:
                    print(str(e))
                    return False
        return True

    def _entry_to_object(self, entry: dict):
        id = entry.pop("_id")
        entry.pop("created_at")
        nodes = entry.pop("nodes")

        s = Sample(**entry)
        s._id = id

        for nodetype, nodeids in nodes.items():
            for nodeid in nodeids:
                if nodetype == "Action":
                    node = self.actionview.get(id=nodeid)
                elif nodetype == "Material":
                    node = self.materialview.get(id=nodeid)
                elif nodetype == "Measurement":
                    node = self.measurementview.get(id=nodeid)
                elif nodetype == "Analysis":
                    node = self.analysisview.get(id=nodeid)
                s.add_node(node)
        s._sort_nodes()

        return s

    def get(self, id: ObjectId) -> Sample:
        entry = self._collection.find_one({"_id": id})
        if entry is None:
            raise NotFoundInDatabaseError(
                f"{self._entry_class.__name__} with id {id} not found in database!"
            )
        return self._entry_to_object(entry)

    def get_by_node(self, node_type: str, node_id: ObjectId) -> List[Sample]:
        """Return any Sample(s) that contain the given node

        Args:
            node_type (str): Type (Action, Material, Measurement, or Analysis) of node
            node_id (ObjectId): ObjectId of node

        Raises:
            ValueError: Invalid node type
            NotFoundInDatabaseError: No Sample found containing specified node

        Returns:
            List[Sample]: List of Sample(s) containing the specified node. List is sorted from most recent to oldest.
        """
        if node_type not in ["Action", "Material", "Measurement", "Analysis"]:
            raise ValueError(
                f"node_type must be one of 'Action', 'Material', 'Measurement', 'Analysis'"
            )

        result = list(self._collection.find({f"nodes.{node_type}": node_id}))
        result.sort(key=lambda x: x["created_at"], reverse=True)
        entries = [self._entry_to_object(entry) for entry in result]
        if len(entries) == 0:
            raise NotFoundInDatabaseError(
                f"No Sample found containing node of type {node_type} with id {node_id}!"
            )
        return entries

    def get_by_action_node(self, action_id: ObjectId) -> List[Sample]:
        return self.get_by_node("Action", action_id)

    def get_by_material_node(self, material_id: ObjectId) -> List[Sample]:
        return self.get_by_node("Material", material_id)

    def get_by_measurement_node(self, measurement_id: ObjectId) -> List[Sample]:
        return self.get_by_node("Measurement", measurement_id)

    def get_by_analysis_node(self, analysis_id: ObjectId) -> List[Sample]:
        return self.get_by_node("Analysis", analysis_id)
