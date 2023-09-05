from typing import List, Optional, Union
from labgraph.data.nodes import (
    Action,
    Analysis,
    Material,
    Measurement,
    Ingredient,
)
from labgraph.utils.data_objects import LabgraphMongoDB
from .base import BaseNodeView
from .actors import Actor, ActorView


class MaterialView(BaseNodeView):
    def __init__(self, labgraph_mongodb_instance: Optional[LabgraphMongoDB] = None):
        super().__init__("materials", Material, labgraph_mongodb_instance=labgraph_mongodb_instance)

class BaseNodeWithActorView(BaseNodeView):
    def get_by_actor(self, actor: Union[Actor, List[Actor]]):
        if isinstance(actor, Actor):
            actor = [actor]
        if not all(isinstance(a, Actor) for a in actor):
            raise TypeError("argument `actor` must be an Actor or a list of Actors!")
        
        actor_ids = [a.id for a in actor]
        return self.filter({"actor_id": {"$in": actor_ids}})
class ActionView(BaseNodeWithActorView):
    def __init__(self, labgraph_mongodb_instance: Optional[LabgraphMongoDB] = None):
        super().__init__("actions", Action, labgraph_mongodb_instance=labgraph_mongodb_instance)

class MeasurementView(BaseNodeWithActorView):
    def __init__(self, labgraph_mongodb_instance: Optional[LabgraphMongoDB] = None):
        super().__init__("measurements", Measurement, labgraph_mongodb_instance=labgraph_mongodb_instance)

class AnalysisView(BaseNodeWithActorView):
    def __init__(self, labgraph_mongodb_instance: Optional[LabgraphMongoDB] = None):
        super().__init__("analyses", Analysis, labgraph_mongodb_instance=labgraph_mongodb_instance)
