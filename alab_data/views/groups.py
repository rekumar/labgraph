from datetime import datetime
from typing import List, cast
from alab_data.data import Action, Analysis, Material, Measurement, Sample
from alab_data.utils.data_objects import get_collection
from alab_data.views.nodes import ActionView, MaterialView, AnalysisView, MeasurementView
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
        if not self.allow_duplicate_names and not found_in_db:
            try:
                self.get_by_name(name=entry.name)
                found_in_db = True
            except ValueError:
                pass  # entry is not in db, we can proceed to add it
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

        checkifvalid_methods = {
            Action: self._is_valid_action,
            Material: self._is_valid_material,
            Measurement: self._is_valid_measurement,
            Analysis: self._is_valid_analysis,
        }
        for node in sample.nodes:
            _is_valid = checkifvalid_methods[type(node)]
            if not _is_valid(node, upcoming_nodes):
                return False
        return True

    def _is_valid_action(self, action: Action, upcoming_nodes: List[ObjectId]) -> bool:
        # check if the action is valid
        for material_id in action.upstream + action.downstream:
            if material_id in upcoming_nodes:
                continue
            try:
                self.materialview.get(id=material_id)
            except NotFoundInDatabaseError as e:
                print(str(e))
                return False
        return True

    def _is_valid_material(
        self, material: Material, upcoming_nodes: List[ObjectId]
    ) -> bool:
        # check if the material is valid
        for id in material.upstream + material.downstream:
            if id in upcoming_nodes:
                continue
            found_in_actions = False
            found_in_measurements = False
            try:
                self.actionview.get(id=id)
                found_in_actions = True
            except NotFoundInDatabaseError as e:
                print(str(e))
                pass
            try:
                self.measurementview.get(id=id)
                found_in_measurements = True
            except NotFoundInDatabaseError as e:
                print(str(e))
                pass
            if not (found_in_actions or found_in_measurements):
                return False  # TODO this is really janky. we need to differentiate material downstream by Action vs Measurement.
        return True

    def _is_valid_measurement(
        self, measurement: Measurement, upcoming_nodes: List[ObjectId]
    ) -> bool:
        # check if the measurement is valid
        for material_id in measurement.upstream:
            if material_id in upcoming_nodes:
                continue
            try:
                self.materialview.get(id=material_id)
            except NotFoundInDatabaseError as e:
                print(str(e))
                return False
        for analysis_id in measurement.downstream:
            if analysis_id in upcoming_nodes:
                continue
            try:
                self.analysisview.get(id=analysis_id)
            except NotFoundInDatabaseError as e:
                print(str(e))
                return False
        return True

    def _is_valid_analysis(
        self, analysis: Analysis, upcoming_nodes: List[ObjectId]
    ) -> bool:
        # check if the analysis is valid
        for measurement_id in analysis.upstream:
            if measurement_id in upcoming_nodes:
                continue
            try:
                self.measurementview.get(id=measurement_id)
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
        return s


# class ExperimentView:
#     """
#     Experiment view manages the experiment status, which is a collection of tasks and samples
#     """

#     def __init__(self):
#         self._experiment_collection = get_collection("experiment")
#         self.action_view = ActionView()
#         self.material_view = MaterialView()
#         self.measurement_view = MeasurementView()
#         self.analysis_view = AnalysisView()
