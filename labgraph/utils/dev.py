def drop_collections():
    from labgraph.views import (
        MaterialView,
        ActionView,
        MeasurementView,
        AnalysisView,
        ActorView,
        SampleView,
    )

    for view in [
        MaterialView(),
        ActionView(),
        MeasurementView(),
        AnalysisView(),
        ActorView(),
        SampleView(),
    ]:
        view._collection.drop()
