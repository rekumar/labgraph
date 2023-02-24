from labgraph.data.nodes import (
    Action,
    Analysis,
    Material,
    Measurement,
    Ingredient,
)
from .base import BaseNodeView
from .actors import ActorView, AnalysisMethodView


class MaterialView(BaseNodeView):
    def __init__(self):
        super().__init__("materials", Material)


class ActionView(BaseNodeView):
    def __init__(self):
        super().__init__("actions", Action)


class MeasurementView(BaseNodeView):
    def __init__(self):
        super().__init__("measurements", Measurement)


class AnalysisView(BaseNodeView):
    def __init__(self):
        super().__init__("analyses", Analysis)
