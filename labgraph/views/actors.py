from labgraph.data.actors import Actor, AnalysisMethod
from labgraph.views.base import BaseActorView


class AnalysisMethodView(BaseActorView):
    def __init__(self):
        super().__init__(
            "analysis_methods", AnalysisMethod, allow_duplicate_names=False
        )


class ActorView(BaseActorView):
    def __init__(self):
        super().__init__("actors", Actor, allow_duplicate_names=False)
