from typing import Optional
from labgraph.utils.data_objects import LabgraphMongoDB
from labgraph.views.base import BaseView


def drop_collections(labgraph_mongodb_instance: Optional[LabgraphMongoDB] = None):
    from labgraph.views import (
        MaterialView,
        ActionView,
        MeasurementView,
        AnalysisView,
        ActorView,
        SampleView,
    )

    for View in [
        MaterialView,
        ActionView,
        MeasurementView,
        AnalysisView,
        ActorView,
        SampleView,
    ]:
        View(labgraph_mongodb_instance=labgraph_mongodb_instance)._collection.drop()