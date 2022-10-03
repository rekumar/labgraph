from alab_data.data import Action, Analysis, Material, Measurement, AnalysisMethod, Actor, Ingredient
from .base import BaseView

class AnalysisMethodView(BaseView):
    def __init__(self):
        super().__init__(
            "analysis_methods", AnalysisMethod, allow_duplicate_names=False
        )


class ActorView(BaseView):
    def __init__(self):
        super().__init__("actors", Actor, allow_duplicate_names=False)

class MaterialView(BaseView):
    def __init__(self):
        super().__init__("materials", Material)



actorview = ActorView()
analysismethodview = AnalysisMethodView()
materialview = MaterialView()

class MeasurementView(BaseView):
    def __init__(self):
        super().__init__("measurements", Measurement)
    
    def _entry_to_object(self, entry: dict):
        actor = actorview.get(id=entry.pop("actor_id"))
        _id = entry.pop("_id")
        entry.pop("created_at")
        upstream_material_id = entry.pop("upstream")[0]["node_id"]
        material = materialview.get(id=upstream_material_id)
        obj = Measurement(material=material, actor=actor, **entry)
        obj._id = _id

        return obj

measurementview = MeasurementView()
class ActionView(BaseView):
    def __init__(self):
        super().__init__("actions", Action)

    def _entry_to_object(self, entry: dict):
        actor = actorview.get(id=entry.pop("actor_id"))
        ingredients = [
            Ingredient(material=materialview.get(id=ing["material_id"]), amount=ing["amount"], unit=ing["unit"], name=ing["name"])
            for ing in entry.pop("ingredients")
        ]
        downstream = entry.pop("downstream")
        generated_materials = [
            materialview.get(id=ds["node_id"]) for ds in downstream
        ]
        upstream = entry.pop("upstream")
        entry.pop("created_at")
        id = entry.pop("_id")
        obj = Action(ingredients = ingredients, generated_materials=generated_materials, actor=actor, **entry)
        obj._id = id
        obj.upstream = upstream
        obj.downstream = downstream

        return obj

class AnalysisView(BaseView):
    def __init__(self):
        super().__init__("analyses", Analysis)

    def _entry_to_object(self, entry: dict):
        method = analysismethodview.get(id=entry.pop("analysismethod_id"))
        id = entry.pop("_id")
        entry.pop("created_at")
        measurements = [
            measurementview.get(id=meas["node_id"])
            for meas in entry.pop("upstream")
        ]
        obj = Analysis(measurements=measurements, analysis_method=method, **entry)
        obj._id = id

        return obj


# class MaterialView(BaseCompositeView):
#     def __init__(self):
#         self.material_view = OnlyMaterialView()
#         self.action_view = OnlyActionView()

#         super(MaterialView, self).__init__(base_collection = self.material_view)

    