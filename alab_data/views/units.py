from alab_data import Action, Analysis, Material, Measurement, AnalysisMethod, Actor
from .base import BaseView


class ActionView(BaseView):
    def __init__(self):
        super().__init__("actions", Action)


class AnalysisView(BaseView):
    def __init__(self):
        super().__init__("analyses", Analysis)


class MaterialView(BaseView):
    def __init__(self):
        super().__init__("materials", Material)


class MeasurementView(BaseView):
    def __init__(self):
        super().__init__("measurements", Measurement)


class AnalysisMethodView(BaseView):
    def __init__(self):
        super().__init__(
            "analysis_methods", AnalysisMethod, allow_duplicate_names=False
        )


class ActorView(BaseView):
    def __init__(self):
        super().__init__("actors", Actor, allow_duplicate_names=False)
