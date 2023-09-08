from typing import Optional
from labgraph.utils.data_objects import LabgraphMongoDB

from labgraph.views import (
        MaterialView,
        ActionView,
        MeasurementView,
        AnalysisView,
        ActorView,
        SampleView,
    )
import numpy as np

def drop_collections(conn: Optional[LabgraphMongoDB] = None):
    

    for View in [
        MaterialView,
        ActionView,
        MeasurementView,
        AnalysisView,
        ActorView,
        SampleView,
    ]:
        View(conn=conn)._collection.drop()
        