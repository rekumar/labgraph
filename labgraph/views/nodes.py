from typing import List, Literal, Optional, Union
from labgraph.data.nodes import (
    Action,
    Analysis,
    Material,
    Measurement,
    Ingredient,
)
from labgraph.errors import NotFoundInDatabaseError
from labgraph.utils.data_objects import LabgraphMongoDB
from .base import BaseNodeView
from .actors import Actor, ActorView


class MaterialView(BaseNodeView):
    def __init__(self, conn: Optional[LabgraphMongoDB] = None):
        super().__init__("materials", Material, conn=conn)

class BaseNodeWithActorView(BaseNodeView):
    def confirm_actors_are_valid(self, actors: List[Actor]):
        """Checks that all actors are valid (i.e. exist in the database)"""
        from labgraph.views import ActorView

        actor_view = ActorView(conn=self._conn)
        for actor in actors:
            if not actor_view._exists(actor.id):
                raise NotFoundInDatabaseError(
                    f"Cannot add node with {actor} because it does not exist in the database!"
                )
    def get_by_actor(self, actor: Union[Actor, List[Actor]]):
        if isinstance(actor, Actor):
            actor = [actor]
        if not all(isinstance(a, Actor) for a in actor):
            raise TypeError("argument `actor` must be an Actor or a list of Actors!")
        
        actor_ids = [a.id for a in actor]
        return self.find({"actor_id": {"$in": actor_ids}})
    
    def add(self, entry, if_already_in_db: Literal["raise", "skip", "update"] = "raise"):
        from labgraph.views import ActorView

        actor_view = ActorView(conn=self._conn)
        for actor in entry.actor:
            if not actor_view._exists(actor.id):
                raise NotFoundInDatabaseError(
                    f"Cannot add {entry} because its actor {actor} does not exist in the database!"
                )
        super().add(entry, if_already_in_db=if_already_in_db)
        
class ActionView(BaseNodeWithActorView):
    def __init__(self, conn: Optional[LabgraphMongoDB] = None):
        super().__init__("actions", Action, conn=conn)
        

class MeasurementView(BaseNodeWithActorView):
    def __init__(self, conn: Optional[LabgraphMongoDB] = None):
        super().__init__("measurements", Measurement, conn=conn)

class AnalysisView(BaseNodeWithActorView):
    def __init__(self, conn: Optional[LabgraphMongoDB] = None):
        super().__init__("analyses", Analysis, conn=conn)
