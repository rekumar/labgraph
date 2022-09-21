def drop_collections():
    from alab_data.views import (
        MaterialView,
        ActionView,
        MeasurementView,
        AnalysisView,
        AnalysisMethodView,
        ActorView,
        SampleView,
    )

    for view in [
        MaterialView(),
        ActionView(),
        MeasurementView(),
        AnalysisView(),
        AnalysisMethodView(),
        ActorView(),
        SampleView(),
    ]:
        view._collection.drop()
