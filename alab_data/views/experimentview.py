from alab_data.utils.data_objects import get_collection
from alab_data.views.action import ActionView
from alab_data.views.analysis import AnalysisView
from alab_data.views.material import MaterialView
from alab_data.views.measurement import MeasurementView


class ExperimentView:
    """
    Experiment view manages the experiment status, which is a collection of tasks and samples
    """

    def __init__(self):
        self._experiment_collection = get_collection("experiment")
        self.action_view = ActionView()
        self.material_view = MaterialView()
        self.measurement_view = MeasurementView()
        self.analysis_view = AnalysisView()
