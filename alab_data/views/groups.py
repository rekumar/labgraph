from datetime import datetime
from typing import cast
from alab_data.units.nodes import Action, Analysis, Material, Measurement
from alab_data.utils.data_objects import get_collection
from alab_data.views import ActionView, MaterialView, AnalysisView, MeasurementView
from alab_data.groups import Sample
from .base import BaseView
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
                f"{self._entry_class.__name__} {entry.name} already exists in the database!"
            )

        # TODO check all nodes before uploading so we dont put half the nodes in before hitting a snag.
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
