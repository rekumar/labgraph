from bson import ObjectId
from typing import List
from .actors import Actor, AnalysisMethod
from abc import ABC, abstractmethod


class BaseObject(ABC):
    def __init__(
        self,
        name: str,
        upstream: List[ObjectId] = None,
        downstream: List[ObjectId] = None,
        tags: List[str] = None,
    ):
        self.name = name
        self._id = ObjectId()
        if upstream is None:
            self.upstream = []
        else:
            self.upstream = upstream
        if downstream is None:
            self.downstream = []
        else:
            self.downstream = downstream
        if tags is None:
            self.tags = []
        else:
            self.tags = tags

    def add_upstream(self, upstream: ObjectId):
        self.upstream.append(upstream)

    def add_downstream(self, downstream: ObjectId):
        self.downstream.append(downstream)

    def to_dict(self):
        mangle_prefix = "_" + self.__class__.__name__
        d = {
            k: v for k, v in self.__dict__.items() if not k.startswith(mangle_prefix)
        }  # dont include double underscored class attributes

        return d

    def to_json(self):
        return self.to_dict()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"
        # return str(self.to_dict())

    @abstractmethod
    def is_valid(self) -> bool:
        """method to validate the object. Necessary before adding to database"""
        raise NotImplementedError

    @property
    def id(self):
        return self._id


## Materials
class Material(BaseObject):
    def __init__(
        self,
        name: str,
        intermediate: bool = False,
        tags: List[str] = None,
        **attributes,
    ):
        super(Material, self).__init__(name=name, tags=tags)
        self.intermediate = intermediate
        self.attributes = attributes

    def is_valid(self) -> bool:
        return True


## Actions
class Ingredient:
    def __init__(self, material: Material, amount: float, unit: str, name: str = None):
        if name is None:
            self.name = material.name
        else:
            self.name = name
        self.material = material
        self.material_id = material.id
        self.amount = amount
        self.unit = unit

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop("material")
        return d


class WholeIngredient(Ingredient):
    """Shortcut for when 100% of a material is consumed by an action. This is common for actions performed on intermediate materials"""

    def __init__(self, material: Material, name: str = None):
        super(WholeIngredient, self).__init__(
            material=material, amount=100, unit="percent", name=name
        )


class Action(BaseObject):
    def __init__(
        self,
        name: str,
        actor: Actor,
        ingredients: List[Ingredient] = [],
        generated_materials: List[Material] = None,
        final: bool = False,
        tags: List[str] = None,
        **parameters,
    ):
        super(Action, self).__init__(name=name, tags=tags)
        self.parameters = parameters
        self.is_final_action = final
        self.__actor = actor
        self.actor_id = actor.id
        self.__materials = set()
        self.ingredients = []
        if len(ingredients) > 0:
            for ingredient in ingredients:
                self.add_ingredient(ingredient)
        # else:
        # if generated_materials is None:
        #     raise ValueError(
        #         "If input material is not specified, the generated material(s) must be specified!"
        #     )
        # if generated_materials is None:
        #     generated_material_name = ""
        #     for ingredient in ingredients:
        #         generated_material_name += ingredient.name + "+"
        #     generated_material_name = generated_material_name[:-1] + " - " + name
        #     self.__generated_materials = [
        #         Material(name=generated_material_name, intermediate=not final)
        #     ]
        # else:
        #     self.__generated_materials = generated_materials

        if generated_materials is None:
            self.__generated_materials = []
        else:
            self.__generated_materials = generated_materials
        for material in self.__generated_materials:
            material.add_upstream(self.id)
            self.add_downstream(material.id)

    def add_ingredient(self, ingredient: Ingredient):
        self.add_upstream(ingredient.material.id)
        ingredient.material.add_downstream(self.id)
        self.__materials.add(ingredient.material.id)
        self.ingredients.append(ingredient.to_dict())

    @property
    def generated_materials(self):
        return self.__generated_materials

    @property
    def actor(self):
        return self.__actor

    def make_generic_generated_material(self):
        if len(self.generated_materials) > 0:
            raise ValueError(
                "Cannot make a generic output Material -- generated Material(s) are already specified!"
            )
        generated_material_name = ""
        for ingredient in self.ingredients:
            generated_material_name += ingredient["name"] + "+"

        if len(generated_material_name) > 0:
            generated_material_name = generated_material_name[:-1] + " - " + self.name
        else:
            generated_material_name = "noingredients - " + self.name

        generic_material = Material(
            name=generated_material_name, intermediate=not self.is_final_action
        )
        generic_material.add_upstream(self.id)
        self.__generated_materials = [generic_material]
        self.add_downstream(generic_material.id)

        return generic_material

    def is_valid(self) -> bool:
        if len(self.generated_materials) == 0:
            self.make_generic_generated_material()
        return True


## Measurements
class Measurement(BaseObject):
    def __init__(
        self,
        name: str,
        material: Material,
        actor: Actor,
        tags: List[str] = None,
        **parameters,
    ):
        super(Measurement, self).__init__(name=name, tags=tags)
        self.parameters = parameters
        self.__material = material
        self.__actor = actor
        self.actor_id = actor.id
        self.material.add_downstream(self.id)
        self.add_upstream(material.id)

    @property
    def material(self):
        return self.__material

    @property
    def actor(self):
        return self.__actor

    def is_valid(self) -> bool:
        return True


## Analyses
class Analysis(BaseObject):
    def __init__(
        self,
        name: str,
        measurements: List[Measurement],
        analysis_method: AnalysisMethod,
        tags: List[str] = None,
        **parameters,
    ):
        super(Analysis, self).__init__(name=name, tags=tags)
        self.__measurements = measurements
        self.parameters = parameters

        for meas in self.__measurements:
            meas.add_downstream(self.id)
            self.add_upstream(meas.id)

        self.analysismethod_id = analysis_method.id
        self.__analysis_method = analysis_method

    @property
    def measurement(self):
        return self.__measurement

    @property
    def analysis_method(self):
        return self.__analysis_method

    def is_valid(self):
        return True
