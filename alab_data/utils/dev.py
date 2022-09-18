def drop_collections():
    from alab_data.views import (
        MaterialView,
        ActionView,
        MeasurementView,
        AnalysisView,
        AnalysisMethodView,
        ActorView,
    )

    for view in [
        MaterialView(),
        ActionView(),
        MeasurementView(),
        AnalysisView(),
        AnalysisMethodView(),
        ActorView(),
    ]:
        view._collection.drop()
