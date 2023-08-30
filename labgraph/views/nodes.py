from typing import List
from labgraph.data.nodes import (
    Action,
    Analysis,
    Material,
    Measurement,
    Ingredient,
)
from .base import BaseNodeView
from .actors import Actor, ActorView


class MaterialView(BaseNodeView):
    def __init__(self):
        super().__init__("materials", Material)


class ActionView(BaseNodeView):
    def __init__(self):
        super().__init__("actions", Action)

    def get_by_actor(self, actor: Actor) -> List[Action]:
        return self.filter({"actor_id": actor.id})


class MeasurementView(BaseNodeView):
    def __init__(self):
        super().__init__("measurements", Measurement)

    def get_by_actor(self, actor: Actor) -> List[Action]:
        return self.filter({"actor_id": actor.id})


class AnalysisView(BaseNodeView):
    def __init__(self):
        super().__init__("analyses", Analysis)

    def get_by_actor(self, actor: Actor) -> List[Action]:
        return self.filter({"actor_id": actor.id})
