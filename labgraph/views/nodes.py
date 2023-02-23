from labgraph.data.nodes import (
    Action,
    Analysis,
    Material,
    Measurement,
    Ingredient,
)
from .base import BaseNodeView
from .actors import ActorView, AnalysisMethodView


class MaterialView(BaseNodeView):
    def __init__(self):
        super().__init__("materials", Material)

    def _entry_to_object(self, entry: dict):
        id = entry.pop("_id")
        version_history = entry.pop("version_history", [])
        entry.pop("created_at")
        entry.pop("updated_at")
        entry.pop("version_history", None)

        us = entry.pop("upstream")
        ds = entry.pop("downstream")

        obj = Material(**entry)
        obj._id = id
        obj._version_history = version_history

        for us_ in us:
            obj.upstream.append(us_)
        for ds_ in ds:
            obj.downstream.append(ds_)

        return obj


class MeasurementView(BaseNodeView):
    def __init__(self):
        super().__init__("measurements", Measurement)
        self._actorview = ActorView()
        self._materialview = MaterialView()

    def _entry_to_object(self, entry: dict):

        actor = self._actorview.get(id=entry.pop("actor_id"))
        _id = entry.pop("_id")
        version_history = entry.pop("version_history", [])

        entry.pop("created_at")
        entry.pop("updated_at")
        version_history = entry.pop("version_history", [])
        upstream_material_id = entry.pop("upstream")[0][
            "node_id"
        ]  # we know each Measurement has exactly one upstream material
        downstream = entry.pop("downstream")
        material = self._materialview.get(id=upstream_material_id)
        obj = Measurement(material=material, actor=actor, **entry)
        obj._id = _id
        obj._version_history = version_history
        for ds in downstream:
            obj.downstream.append(ds)
        obj._version_history = version_history

        return obj


class ActionView(BaseNodeView):
    def __init__(self):
        super().__init__("actions", Action)
        self._actorview = ActorView()
        self._materialview = MaterialView()

    def _entry_to_object(self, entry: dict):
        actor = self._actorview.get(id=entry.pop("actor_id"))
        ingredients = [
            Ingredient(
                material=self._materialview.get(id=ing["material_id"]),
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
        generated_materials = [
            self._materialview.get(id=ds["node_id"]) for ds in downstream
        ]
        obj = Action(
            ingredients=ingredients,
            generated_materials=generated_materials,
            actor=actor,
            **entry
        )
        obj._id = _id
        for us in upstream:
            obj.upstream.append(us)
        for ds in downstream:
            obj.downstream.append(ds)
        obj._version_history = version_history

        return obj


class AnalysisView(BaseNodeView):
    def __init__(self):
        super().__init__("analyses", Analysis)
        self._analysismethodview = AnalysisMethodView()
        self._measurementview = MeasurementView()

    def _entry_to_object(self, entry: dict):
        method = self._analysismethodview.get(id=entry.pop("analysismethod_id"))
        id = entry.pop("_id")
        version_history = entry.pop("version_history", [])

        entry.pop("created_at")
        entry.pop("updated_at")
        upstream = entry.pop("upstream")
        downstream = entry.pop("downstream")
        measurements = [
            self._measurementview.get(id=meas["node_id"])
            for meas in upstream
            if meas["node_type"] == "Measurement"
        ]
        upstream_analyses = [
            self.get(id=ana["node_id"])
            for ana in upstream
            if ana["node_type"] == "Analysis"
        ]
        obj = Analysis(
            measurements=measurements,
            upstream_analyses=upstream_analyses,
            analysis_method=method,
            **entry
        )
        obj._id = id
        for us in upstream:
            obj.upstream.append(us)
        for ds in downstream:
            obj.downstream.append(ds)
        obj._version_history = version_history

        return obj
