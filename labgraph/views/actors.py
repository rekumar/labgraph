from typing import Optional
from labgraph.data.actors import Actor
from labgraph.utils.data_objects import LabgraphMongoDB
from labgraph.views.base import BaseActorView


class ActorView(BaseActorView):
    def __init__(self, labgraph_mongodb_instance: Optional[LabgraphMongoDB] = None):
        super().__init__("actors", Actor, labgraph_mongodb_instance=labgraph_mongodb_instance, allow_duplicate_names=False)
