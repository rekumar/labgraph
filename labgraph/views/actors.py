from typing import Optional
from labgraph.data.actors import Actor
from labgraph.utils.data_objects import LabgraphMongoDB
from labgraph.views.base import BaseActorView


class ActorView(BaseActorView):
    def __init__(self, conn: Optional[LabgraphMongoDB] = None):
        super().__init__("actors", Actor, conn=conn, allow_duplicate_names=False)
