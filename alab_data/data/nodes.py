import datetime
from bson import ObjectId, BSON
from typing import Any, Dict, List, Optional, Union
from .actors import Actor, AnalysisMethod
from abc import ABC, abstractmethod


class BaseObject(ABC):
    def __init__(
        self,
        name: str,
        upstream: List[Dict[str, ObjectId]] = None,
        downstream: List[Dict[str, ObjectId]] = None,
        tags: List[str] = None,
    ):
        self.name = name
        self._id = ObjectId()
        if upstream is None:
            self.upstream = []
        else:
            for us in upstream:
                self.add_upstream(us)
        if downstream is None:
            self.downstream = []
        else:
            for ds in downstream:
                self.add_downstream(ds)
        if tags is None:
            self.tags = []
        else:
            self.tags = tags

    def add_upstream(self, upstream: "BaseObject"):
        if not isinstance(upstream, BaseObject):
            raise TypeError("Upstream nodes must be a BaseObject")

        self.upstream.append(
            {"node_type": upstream.__class__.__name__, "node_id": upstream._id}
        )

    def add_downstream(self, downstream: "BaseObject"):
        if not isinstance(downstream, BaseObject):
            raise TypeError("Upstream nodes must be a BaseObject")
        self.downstream.append(
            {"node_type": downstream.__class__.__name__, "node_id": downstream._id}
        )

    def to_dict(self):
        mangle_prefix = "_" + self.__class__.__name__
        d = {
            k: v for k, v in self.__dict__.items() if not k.startswith(mangle_prefix)
        }  # dont include double underscored class attributes
        params = d.pop("parameters", {})
        params.pop("version_history", None)

        for key in params:
            if key in d:
                raise ValueError(
                    f"Parameter name {key} in node {self.name} of type {self.__class__} conflicts with default node attribute {key} -- please rename the parameter!"
                )
        d.update(params)

        return d

    def is_valid_for_mongodb(self) -> bool:
        """Checks if the object can be converted to BSON. This is a requirement for MongoDB

        Returns:
            bool: True if the object can be converted to BSON and successfully inserted into MongoDB
        """
        d = self.to_dict()
        try:
            BSON.encode(d)
            return True
        except TypeError:
            return False

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

    def __hash__(self):
        return hash(self.name + str(self.id))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.id == self.id


## Materials
class Material(BaseObject):
    """Class to define a Material node. These nodes capture information about a material in a given state. Each Material is created by an Action. Measurements can act upon a Material to yield raw characterization data."""

    def __init__(
        self,
        name: str,
        tags: Optional[Union[List[str], None]] = None,
        **parameters,
    ):
        """Initialize a Material node. This creates the node in memory -- it is not added to the database yet!

        Args:
            name (str): Name of this Material. This is purely for human readability, and does not need to be unique.
            tags (Optional[Union[List[str], None]], optional): A list of tags to catalog this Material. If None (default), no tags will be applied. Tags can be an easy way to query nodes.
            **parameters: Any additional values to be stored in the node. These will be stored as key-value pairs in the node entry in the database. While these values are not used by the database, they can be useful for storing additional information about the node according to user needs. All values within these parameters must be BSON-serializable (e.g. no numpy arrays, etc.) such that they can be stored using MongoDB.
        """
        super(Material, self).__init__(name=name, tags=tags)
        self.parameters = parameters

    def is_valid(self) -> bool:
        for node in self.upstream:
            if node["node_type"] != "Action":
                return False
        for node in self.downstream:
            if node["node_type"] not in ["Action", "Measurement"]:
                return False
        return True

    def _entry_to_object(self, entry: Dict) -> "Material":
        upstream = entry.pop("upstream")
        downstream = entry.pop("downstream")
        _id = entry.pop("_id")
        entry.pop("created_at")

        obj = Material(**entry)
        obj._id = _id
        obj.upstream = upstream
        obj.downstream = downstream
        return obj


## Actions
class Ingredient:
    def __init__(
        self,
        material: Material,
        amount: float,
        unit: str,
        name: str = None,
        **parameters,
    ):
        """

        Args:
            material (Material): Material node that this ingredient is made of.
            amount (float): amount of the material in this ingredient
            unit (str): unit of the amount
            name (str, optional): Name of this ingredient. This differs from the Material name. For example, a Material "cheese" may be an Ingredient named "topping" in a "Make Pizza" action.. Defaults to None.

        Raises:
            TypeError: _description_
        """
        if name is None:
            self.name = material.name
        else:
            self.name = name
        if not isinstance(material, Material):
            raise TypeError(
                'The "material" argument to an Ingredient must be of type `alab_data.nodes.Material`!'
            )
        self.material = material
        self.material_id = material.id
        self.amount = amount
        self.unit = unit
        self.parameters = parameters

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop("material")
        parameters = d.pop("parameters", {})
        for key in parameters:
            if key in d:
                raise ValueError(
                    f"Parameter name {key} in Ingredient conflicts with default attribute {key} -- please rename the parameter!"
                )
        d.update(parameters)
        return d

    def __repr__(self):
        s = f"<Ingredient: {self.name} ({self.amount} {self.unit} of {self.material})>"
        return s


class WholeIngredient(Ingredient):
    def __init__(self, material: Material, name: str = None, **parameters):
        """Shortcut for when 100% of a material is consumed by an action. This is common for actions performed on intermediate materials.

        Args:
            material (Material): Material node described by this ingredient.
            name (str, optional): Name of this ingredient. This differs from the Material name. For example, a Material "cheese" may be an Ingredient named "topping" in a "Make Pizza" action. Defaults to None.
        """
        super(WholeIngredient, self).__init__(
            material=material, amount=100, unit="percent", name=name, **parameters
        )


class Action(BaseObject):
    def __init__(
        self,
        name: str,
        actor: Actor,
        ingredients: List[Ingredient] = [],
        generated_materials: List[Material] = None,
        tags: List[str] = None,
        **parameters,
    ):
        """Generates an Action node. Actions create new Material(s), optionally using existing Material(s) in the form of Ingredient(s). Actions are the primary way to create new Material nodes in the database.

        Args:
            name (str): Name of the Action node.
            actor (Actor): Actor which performs this Action.
            ingredients (List[Ingredient], optional): List of Ingredient objects, which describes a Material node with the amount of Material used in this Action. Defaults to [].
            generated_materials (List[Material], optional): Material Node(s) created by this Action. Defaults to None.
            tags (List[str], optional): List of string tags used to identify this Action node. Defaults to None.
        """
        super(Action, self).__init__(name=name, tags=tags)
        self.parameters = parameters
        self.__actor = actor
        self.actor_id = actor.id
        # self.__materials = set()
        self.ingredients = []
        if len(ingredients) > 0:
            for ingredient in ingredients:
                self.add_ingredient(ingredient)

        if generated_materials is None:
            self.__generated_materials = []
        else:
            self.__generated_materials = generated_materials
        for material in self.__generated_materials:
            material.add_upstream(self)
            self.add_downstream(material)

    def add_ingredient(self, ingredient: Ingredient):
        if not isinstance(ingredient, Ingredient):
            raise TypeError(
                "All ingredients must be of type `alab_data.nodes.Ingredient`!"
            )
        self.add_upstream(ingredient.material)
        ingredient.material.add_downstream(self)
        # self.__materials.add(ingredient.material)
        self.ingredients.append(ingredient)

    def add_generated_material(self, material: Material):
        if not isinstance(material, Material):
            raise TypeError(
                "All generated materials must be of type `alab_data.nodes.Material`!"
            )
        self.add_downstream(material)
        material.add_upstream(self)
        self.__generated_materials.append(material)

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
            generated_material_name += ingredient.name + "+"

        if len(generated_material_name) > 0:
            generated_material_name = generated_material_name[:-1] + " - " + self.name
        else:
            generated_material_name = "noingredients - " + self.name

        generic_material = Material(name=generated_material_name)
        generic_material.add_upstream(self)
        self.__generated_materials = [generic_material]
        self.add_downstream(generic_material)

        return generic_material

    def is_valid(self) -> bool:
        # TODO do we want to enforce a created material? Or can we "destroy" materials via actions, ie a waste stream?
        for node in self.upstream + self.downstream:
            if node["node_type"] != "Material":
                return False
        # if len(self.generated_materials) == 0:
        #     self.make_generic_generated_material()
        return True

    def _entry_to_object(self, entry: Dict) -> "Action":
        upstream = entry.pop("upstream")
        downstream = entry.pop("downstream")
        _id = entry.pop("_id")
        entry.pop("created_at")

        ingredients = [
            Ingredient(
                name=i["name"],
                material_id=i["material_id"],
                amount=i["amount"],
                unit=i["unit"],
            )
            for i in entry.pop("ingredients")
        ]

        obj = Action(ingredients=ingredients, **entry)
        obj._id = _id
        obj.upstream = upstream
        obj.downstream = downstream
        return obj

    def to_dict(self):
        d = super(Action, self).to_dict()
        ingredients = d.pop("ingredients")
        d["ingredients"] = [i.to_dict() for i in ingredients]

        return d


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
        """A Measurement Node. This is a node that represents a measurement of a material by an actor.

        Args:
            name (str): Name of the measurement.
            material (Material): Material node upon which this Measurement is performed.
            actor (Actor): Actor which performs the measurement.
            tags (List[str], optional): List of string tags to identify this node. Defaults to None.

        Raises:
            TypeError: Invalid type for `material` argument.
        """
        super(Measurement, self).__init__(name=name, tags=tags)
        if not isinstance(material, Material):
            raise TypeError(
                "The `material` argument to a Measurement must be of type `alab_data.nodes.Material`!"
            )
        self.parameters = parameters
        self.__material = material
        self.__actor = actor
        self.actor_id = actor.id
        self.material.add_downstream(self)
        self.add_upstream(material)

    @property
    def material(self):
        return self.__material

    @property
    def actor(self):
        return self.__actor

    def is_valid(self) -> bool:
        for node in self.upstream:
            if node["node_type"] != "Material":
                return False
        for node in self.downstream:
            if node["node_type"] != "Analysis":
                return False
        return True


## Analyses
class Analysis(BaseObject):
    def __init__(
        self,
        name: str,
        analysis_method: AnalysisMethod,
        measurements: List[Measurement] = None,
        upstream_analyses: List["Analysis"] = None,
        tags: List[str] = None,
        **parameters,
    ):
        """Creates an Analysis node. This node represents data processing from upstream Measurement(s) and/or Analysis/es node(s). For example, a "Density" Analysis may accept "Mass" and "Volume" measurements to compute density.

        Args:
            name (str): Name of the Analysis node.
            measurements (List[Measurement]): Measurements, if any, on which this Analysis is based. Defaults to None. At least one upstream measurement or analysis must be provided.
            upstream_analyses (List[Analysis]): Analysis node(s), if any, on which this Analysis is based. Defaults to None. At least one upstream measurement or analysis must be provided.
            analysis_method (AnalysisMethod): AnalysisMethod describing how this analysis was performed.
            tags (List[str], optional): List of string tags. Defaults to None.

        Raises:
            TypeError: Invalid node type passed to `measurements` or `analyses` arguments.
        """
        super(Analysis, self).__init__(name=name, tags=tags)
        self.__measurements = measurements
        self.__upstream_analyses = upstream_analyses
        self.parameters = parameters

        if len(measurements) + len(upstream_analyses) == 0:
            raise ValueError(
                "At least one upstream measurement or analysis must be provided!"
            )
        for meas in self.__measurements:
            if not isinstance(meas, Measurement):
                raise TypeError(
                    "All measurements must be of type `alab_data.nodes.Measurement`!"
                )
            meas.add_downstream(self)
            self.add_upstream(meas)

        for analysis in upstream_analyses:
            if not isinstance(analysis, Analysis):
                raise TypeError(
                    "All analyses must be of type `alab_data.nodes.Analysis`!"
                )
            analysis.add_downstream(self)
            self.add_upstream(analysis)
        self.analysismethod_id = analysis_method.id
        self.__analysis_method = analysis_method

    @property
    def measurements(self):
        return self.__measurements

    @property
    def upstream_analyses(self):
        return self.__upstream_analyses

    @property
    def analysis_method(self):
        return self.__analysis_method

    def is_valid(self) -> bool:
        for node in self.upstream:
            if node["node_type"] != "Measurement":
                return False
        for node in self.downstream:
            if node["node_type"] != "Analysis":
                return False
        return True
