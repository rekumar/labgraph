from labgraph.data.actors import Actor
from labgraph.views.base import BaseActorView


class ActorView(BaseActorView):
    def __init__(self):
        super().__init__("actors", Actor, allow_duplicate_names=False)
