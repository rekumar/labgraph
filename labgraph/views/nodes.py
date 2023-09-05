from typing import List, Union
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

class BaseNodeWithActorView(BaseNodeView):
    def get_by_actor(self, actor: Union[Actor, List[Actor]]):
        if isinstance(actor, Actor):
            actor = [actor]
        if not all(isinstance(a, Actor) for a in actor):
            raise TypeError("argument `actor` must be an Actor or a list of Actors!")
        
        actor_ids = [a.id for a in actor]
        return self.filter({"actor_id": {"$in": actor_ids}})
class ActionView(BaseNodeWithActorView):
    def __init__(self):
        super().__init__("actions", Action)

class MeasurementView(BaseNodeWithActorView):
    def __init__(self):
        super().__init__("measurements", Measurement)

class AnalysisView(BaseNodeWithActorView):
    def __init__(self):
        super().__init__("analyses", Analysis)
