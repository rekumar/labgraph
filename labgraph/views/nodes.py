from labgraph.data.nodes import (
    Action,
    Analysis,
    Material,
    Measurement,
    Ingredient,
)
from .base import BaseNodeView
from .actors import ActorView, AnalysisMethodView

actorview = ActorView()
analysismethodview = AnalysisMethodView()


class MaterialView(BaseNodeView):
    def __init__(self):
        super().__init__("materials", Material)

    def _entry_to_object(self, entry: dict):
        id = entry.pop("_id")
        version_history = entry.pop("version_history", [])
        entry.pop("created_at")
        entry.pop("updated_at")
        entry.pop("version_history", None)

        is_dag_node = "upstream" in entry
        if is_dag_node:
            us = entry.pop("upstream")
            ds = entry.pop("downstream")

        obj = Material(**entry)
        obj._id = id

        if is_dag_node:
            obj.upstream = us
            obj.downstream = ds

        obj._version_history = version_history

        return obj


materialview = MaterialView()


class MeasurementView(BaseNodeView):
    def __init__(self):
        super().__init__("measurements", Measurement)

    def _entry_to_object(self, entry: dict):
        actor = actorview.get(id=entry.pop("actor_id"))
        _id = entry.pop("_id")
        version_history = entry.pop("version_history", [])

        entry.pop("created_at")
        entry.pop("updated_at")
        version_history = entry.pop("version_history", [])
        upstream_material_id = entry.pop("upstream")[0][
            "node_id"
        ]  # we know each Measurement has exactly one upstream material
        downstream = entry.pop("downstream")
        material = materialview.get(id=upstream_material_id)
        obj = Measurement(material=material, actor=actor, **entry)
        obj._id = _id
        obj._version_history = version_history
        obj.downstream = downstream
        obj._version_history = version_history

        return obj


measurementview = MeasurementView()


class ActionView(BaseNodeView):
    def __init__(self):
        super().__init__("actions", Action)

    def _entry_to_object(self, entry: dict):
        actor = actorview.get(id=entry.pop("actor_id"))
        ingredients = [
            Ingredient(
                material=materialview.get(id=ing["material_id"]),
                amount=ing["amount"],
                unit=ing["unit"],
                name=ing["name"],
            )
            for ing in entry.pop("ingredients")
        ]
        _id = entry.pop("_id")
        version_history = entry.pop("version_history", [])
        entry.pop("created_at")
        entry.pop("updated_at")
        entry.pop("version_history", None)
        upstream = entry.pop("upstream")
        downstream = entry.pop("downstream")
        generated_materials = [materialview.get(id=ds["node_id"]) for ds in downstream]
        obj = Action(
            ingredients=ingredients,
            generated_materials=generated_materials,
            actor=actor,
            **entry
        )
        obj._id = _id
        obj.upstream = upstream
        obj.downstream = downstream
        obj._version_history = version_history

        return obj


class AnalysisView(BaseNodeView):
    def __init__(self):
        super().__init__("analyses", Analysis)

    def _entry_to_object(self, entry: dict):
        method = analysismethodview.get(id=entry.pop("analysismethod_id"))
        id = entry.pop("_id")
        version_history = entry.pop("version_history", [])

        entry.pop("created_at")
        entry.pop("updated_at")
        entry.pop("version_history", None)
        upstream = entry.pop("upstream")
        downstream = entry.pop("downstream")
        measurements = [measurementview.get(id=meas["node_id"]) for meas in upstream]
        obj = Analysis(measurements=measurements, analysis_method=method, **entry)
        obj._id = id
        obj.upstream = upstream
        obj.downstream = downstream
        obj._version_history = version_history

        return obj
