import datetime
from bson import ObjectId, BSON
from typing import Any, Dict, List, Optional, Union
from .actors import Actor, AnalysisMethod
from abc import ABC, abstractmethod


class NodeList(list):
    """This is used to store lists of nodes. Nodes are stored as dicts with the node type and key. This prevents cascading database calls to retrieve nodes across a graph.

    However the user can append node objects directly, and the NodeList will convert them to dicts. Furthermore, users can retrieve the node objects with the .get() method.
    """

    def append(self, value: Union["BaseNode", Dict[str, Any]]):
        """Append a node to the NodeList

        Args:
            value (Union[BaseNode, Dict[str, Any]]): Either a Node instance (Material, Measurement, Analysis, Action) or a dict with keys 'node_type' and 'node_id'. If a dict is passed, it must have the correct keys. (This is to prevent accidental appending of dicts that are not nodes.

        Raises:
            ValueError: Invalid node entry/dict.
        """
        if isinstance(value, BaseNode):
            super().append(
                {
                    "node_type": value.__class__.__name__,
                    "node_id": value._id,
                }
            )
        elif isinstance(value, dict):
            if not all([k in value for k in ["node_type", "node_id"]]):
                raise ValueError(
                    "Invalid node entry. Dicts appended to NodeList must have keys 'node_type' and 'node_id'"
                )
            super().append(
                {
                    "node_type": value["node_type"],
                    "node_id": value["node_id"],
                }
            )
        else:
            raise ValueError(
                "Invalid node entry. NodeList can only contain BaseNode instances or dicts with keys 'node_type' and 'node_id'"
            )

    def get(self, index: Optional[int] = None) -> Union["BaseNode", List["BaseNode"]]:
        """Get a node object from the NodeList. If an index is passed, the node at that index is returned. If no index is passed, a list of all nodes is returned.

        Args:
            index (Optional[int], optional): Index of node to retrieve. Defaults to None, in which case the entire list is returned as a list of node objects.

        Returns:
            Union[BaseNode, List[BaseNode]]: Either a single node object, or a list of node objects. Depends on whether an index is passed.
        """
        from labgraph.views import (
            MaterialView,
            MeasurementView,
            AnalysisView,
            ActionView,
        )

        VIEWS = {
            "Material": MaterialView,
            "Measurement": MeasurementView,
            "Analysis": AnalysisView,
            "Action": ActionView,
        }

        if index is not None:
            entry = self[index]
            node_type = entry["node_type"]
            node_id = entry["node_id"]
            view = VIEWS[node_type]()
            return view.get(id=node_id)

        node_objects = []
        for entry in self:
            node_type = entry["node_type"]
            node_id = entry["node_id"]
            view = VIEWS[node_type]()
            node_objects.append(view.get(id=node_id))
        return node_objects


class BaseNode(ABC):
    def __init__(
        self,
        name: str,
        upstream: List[Dict[str, ObjectId]] = None,
        downstream: List[Dict[str, ObjectId]] = None,
        tags: List[str] = None,
    ):
        self.name = name
        self._id = ObjectId()
        self.upstream = NodeList()
        self.downstream = NodeList()
        for us in upstream or []:
            self.upstream.append(us)
        for ds in downstream or []:
            self.downstream.append(ds)
        if tags is None:
            self.tags = []
        else:
            self.tags = tags

        self._version_history = []
        self._user_fields = {}

    def add_upstream(self, upstream: "BaseNode"):
        if not isinstance(upstream, BaseNode):
            raise TypeError("Upstream nodes must be a BaseObject")

        new_entry = {"node_type": upstream.__class__.__name__, "node_id": upstream._id}
        if new_entry not in self.upstream:
            self.upstream.append(new_entry)

    def add_downstream(self, downstream: "BaseNode"):
        if not isinstance(downstream, BaseNode):
            raise TypeError("Upstream nodes must be a BaseObject")
        new_entry = {
            "node_type": downstream.__class__.__name__,
            "node_id": downstream._id,
        }
        if new_entry not in self.downstream:
            self.downstream.append(new_entry)

    def to_dict(self):
        mangle_prefix = "_" + self.__class__.__name__
        d = {
            k: v for k, v in self.__dict__.items() if not k.startswith(mangle_prefix)
        }  # dont include double underscored class attributes
        d.pop("_version_history", None)
        d["version_history"] = self.version_history
        params = d.pop("_user_fields", {})

        for key in params:
            if key in d:
                raise ValueError(
                    f"User field {key} in node {self.name} of type {self.__class__} conflicts with default node attribute {key} -- please rename the parameter!"
                )
        d.update(params)

        return d

    @classmethod
    @abstractmethod
    def from_dict(cls, d: Dict[str, Any]):
        raise NotImplementedError

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

    @abstractmethod
    def is_valid(self) -> bool:
        """method to validate the object. Necessary before adding to database"""
        raise NotImplementedError

    @property
    def id(self):
        return self._id

    @property
    def version_history(self):
        return self._version_history

    def __hash__(self):
        return hash(self.name + str(self.id))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.id == self.id

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def save(self):
        view = self.__get_view()
        view.add(entry=self, if_already_in_db="update")

    @classmethod
    def __get_view(cls):
        from labgraph.views import (
            MaterialView,
            MeasurementView,
            AnalysisView,
            ActionView,
        )

        VIEWS = {
            "Material": MaterialView,
            "Measurement": MeasurementView,
            "Analysis": AnalysisView,
            "Action": ActionView,
        }
        view = VIEWS[cls.__name__]()
        return view

    def __getitem__(self, key: str):
        return self._user_fields[key]

    def __setitem__(self, key: str, value: Any):
        self._user_fields[key] = value

    def keys(self):
        return list(self._user_fields.keys())

    @classmethod
    def get(cls, id: ObjectId) -> "BaseNode":
        """Get a node from the database by id

        Args:
            id (str): id of the node

        Returns:
            BaseNode: Node object with the given id
        """
        view = cls.__get_view()
        return view.get(id)

    @classmethod
    def get_by_name(cls, name: str) -> List["BaseNode"]:
        """Get a node from the database by name

        Args:
            name (str): name of the node. Note that node names are not unique, so multiple nodes may be returned.

        Returns:
            List[BaseNode]: List of node objects with the given name
        """
        view = cls.__get_view()
        return view.get_by_name(name)

    @classmethod
    def get_by_tags(cls, tags: List[str]) -> List["BaseNode"]:
        """Get a node from the database by tags

        Args:
            tags (List[str]): tags of the node. Only nodes with all of the given tags will be returned.

        Returns:
            List[BaseNode]: List of node objects with the given tags.
        """
        view = cls.__get_view()
        return view.get_by_tags(tags)

    @classmethod
    def filter(
        cls,
        filter_dict: dict,
        datetime_min: datetime = None,
        datetime_max: datetime = None,
    ) -> List["BaseNode"]:
        """Thin wrapper around pymongo find method, with an extra datetime filter.

        Args:
            filter_dict (Dict): standard mongodb filter dictionary.
            datetime_min (datetime, optional): entries from before this datetime will not be shown. Defaults to None.
            datetime_max (datetime, optional): entries from after this datetime will not be shown. Defaults to None.

        Returns:
            List[BaseObject]: List of nodes that match the filter
        """
        view = cls.__get_view()
        return view.filter(filter_dict, datetime_min, datetime_max)

    @classmethod
    def filter_one(
        cls,
        filter_dict: dict,
        datetime_min: datetime = None,
        datetime_max: datetime = None,
    ) -> "BaseNode":
        """Thin wrapper around pymongo find_one method, with an extra datetime filter.

        Args:
            filter_dict (Dict): standard mongodb filter dictionary.
            datetime_min (datetime, optional): entries from before this datetime will not be shown. Defaults to None.
            datetime_max (datetime, optional): entries from after this datetime will not be shown. Defaults to None.

        Returns:
            BaseObject: Node that matches the filter
        """
        view = cls.__get_view()
        return view.filter_one(filter_dict, datetime_min, datetime_max)


## Materials
class Material(BaseNode):
    """Class to define a Material node. These nodes capture information about a material in a given state. Each Material is created by an Action. Measurements can act upon a Material to yield raw characterization data."""

    def __init__(
        self,
        name: str,
        tags: Optional[Union[List[str], None]] = None,
        **user_fields,
    ):
        """Initialize a Material node. This creates the node in memory -- it is not added to the database yet!

        Args:
            name (str): Name of this Material. This is purely for human readability, and does not need to be unique.
            tags (Optional[Union[List[str], None]], optional): A list of tags to catalog this Material. If None (default), no tags will be applied. Tags can be an easy way to query nodes.
            **user_fields: Any additional values to be stored in the node. These will be stored as key-value pairs in the node entry in the database. While these values are not used by the database, they can be useful for storing additional information about the node according to user needs. All values within these fields must be BSON-serializable (e.g. no numpy arrays, etc.) such that they can be stored using MongoDB.
        """
        super(Material, self).__init__(name=name, tags=tags)
        self._user_fields = user_fields

    def is_valid(self) -> bool:
        for node in self.upstream:
            if node["node_type"] != "Action":
                return False
        for node in self.downstream:
            if node["node_type"] not in ["Action", "Measurement"]:
                return False
        return True

    @classmethod
    def from_dict(cls, entry: dict) -> "Material":
        _id = entry.pop("_id", None)
        version_history = entry.pop("version_history", [])
        entry.pop("created_at", None)
        entry.pop("updated_at", None)
        entry.pop("version_history", None)

        us = entry.pop("upstream")
        ds = entry.pop("downstream")

        obj = cls(**entry)
        if _id is not None:
            obj._id = _id
        obj._version_history = version_history

        for us_ in us:
            obj.upstream.append(us_)
        for ds_ in ds:
            obj.downstream.append(ds_)

        return obj


## Actions
class Ingredient:
    def __init__(
        self,
        material: Material,
        amount: float,
        unit: str,
        name: str = None,
        **user_fields,
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
                'The "material" argument to an Ingredient must be of type `labgraph.nodes.Material`!'
            )
        self.material = material
        self.material_id = material.id
        self.amount = amount
        self.unit = unit
        self._user_fields = user_fields

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop("material")
        user_fields = d.pop("_user_fields", {})
        for key in user_fields:
            if key in d:
                raise ValueError(
                    f"Parameter name {key} in Ingredient conflicts with default attribute {key} -- please rename the parameter!"
                )
        d.update(user_fields)
        return d

    def __repr__(self):
        s = f"<Ingredient: {self.name} ({self.amount} {self.unit} of {self.material})>"
        return s


class WholeIngredient(Ingredient):
    def __init__(self, material: Material, name: str = None, **user_fields):
        """Shortcut for when 100% of a material is consumed by an action. This is common for actions performed on intermediate materials.

        Args:
            material (Material): Material node described by this ingredient.
            name (str, optional): Name of this ingredient. This differs from the Material name. For example, a Material "cheese" may be an Ingredient named "topping" in a "Make Pizza" action. Defaults to None.
        """
        super(WholeIngredient, self).__init__(
            material=material, amount=100, unit="percent", name=name, **user_fields
        )


class Action(BaseNode):
    def __init__(
        self,
        name: str,
        actor: Actor,
        ingredients: List[Ingredient] = [],
        generated_materials: List[Material] = None,
        tags: List[str] = None,
        **user_fields,
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
        self._user_fields = user_fields
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
                "All ingredients must be of type `labgraph.nodes.Ingredient`!"
            )
        self.add_upstream(ingredient.material)
        ingredient.material.add_downstream(self)
        # self.__materials.add(ingredient.material)
        self.ingredients.append(ingredient)

    def add_generated_material(self, material: Material):
        if not isinstance(material, Material):
            raise TypeError(
                "All generated materials must be of type `labgraph.nodes.Material`!"
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

    def make_generic_generated_material(self, name: Optional[str] = None) -> Material:
        """Creates a generic Material node that is generated by this Action. This is useful for when you want to create a Material node that is generated by this Action, but you don't want to specify the exact Material node that is generated. This is common when you have a sequence of Actions (which require intervening Materials to be valid Labgraph entries), but where you did not perform any measurements or othe operations on the intermediate Materials.

        Args:
            name (Optional[str], optional): The name of the generated Material. If you leave this blank, Labgraph will use the names of this Action and its Ingredients to create a generic name. Defaults to None.

        Raises:
            ValueError: This Action already has generated Materials associated with it, so we can't make a catch-all generic Material node.

        Returns:
            Material: the generated Material object.
        """
        if len(self.generated_materials) > 0:
            raise ValueError(
                "Cannot make a generic output Material -- generated Material(s) are already specified!"
            )
        if name is None:
            generated_material_name = ""
            for ingredient in self.ingredients:
                generated_material_name += ingredient.name + "+"

            if len(generated_material_name) > 0:
                generated_material_name = (
                    generated_material_name[:-1] + " - " + self.name
                )
            else:
                generated_material_name = "noingredients - " + self.name
        else:
            generated_material_name = name

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

    def to_dict(self):
        d = super(Action, self).to_dict()
        ingredients = d.pop("ingredients")
        d["ingredients"] = [i.to_dict() for i in ingredients]

        return d

    @classmethod
    def from_dict(cls, entry: dict) -> "Action":
        from labgraph.views import ActorView
        from labgraph.views import MaterialView

        mv = MaterialView()
        actor = ActorView().get(id=entry.pop("actor_id"))
        ingredients = [
            Ingredient(
                material=mv.get(id=ing["material_id"]),
                amount=ing["amount"],
                unit=ing["unit"],
                name=ing["name"],
            )
            for ing in entry.pop("ingredients")
        ]
        _id = entry.pop("_id", None)
        version_history = entry.pop("version_history", [])
        entry.pop("created_at", None)
        entry.pop("updated_at", None)
        entry.pop("version_history", None)
        upstream = entry.pop("upstream")
        downstream = entry.pop("downstream")
        generated_materials = [mv.get(id=ds["node_id"]) for ds in downstream]
        obj = cls(
            ingredients=ingredients,
            generated_materials=generated_materials,
            actor=actor,
            **entry,
        )
        if _id:
            obj._id = _id
        for us in upstream:
            obj.upstream.append(us)
        for ds in downstream:
            obj.downstream.append(ds)
        obj._version_history = version_history

        return obj


## Measurements
class Measurement(BaseNode):
    def __init__(
        self,
        name: str,
        material: Material,
        actor: Actor,
        tags: List[str] = None,
        **user_fields,
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
                "The `material` argument to a Measurement must be of type `labgraph.nodes.Material`!"
            )
        self._user_fields = user_fields
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

    @classmethod
    def from_dict(cls, entry: dict) -> "Measurement":
        from labgraph.views import ActorView
        from labgraph.views import MaterialView

        actor = ActorView().get(id=entry.pop("actor_id"))
        _id = entry.pop("_id", None)
        version_history = entry.pop("version_history", [])

        entry.pop("created_at", None)
        entry.pop("updated_at", None)
        version_history = entry.pop("version_history", [])
        upstream_material_id = entry.pop("upstream")[0][
            "node_id"
        ]  # we know each Measurement has exactly one upstream material
        downstream = entry.pop("downstream")
        material = MaterialView().get(id=upstream_material_id)
        obj = cls(material=material, actor=actor, **entry)
        if _id is not None:
            obj._id = _id
        obj._version_history = version_history
        for ds in downstream:
            obj.downstream.append(ds)
        obj._version_history = version_history

        return obj


## Analyses
class Analysis(BaseNode):
    def __init__(
        self,
        name: str,
        analysis_method: AnalysisMethod,
        measurements: List[Measurement] = None,
        upstream_analyses: List["Analysis"] = None,
        tags: List[str] = None,
        **user_fields,
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
        measurements = measurements or []
        upstream_analyses = upstream_analyses or []

        if len(measurements) + len(upstream_analyses) == 0:
            raise ValueError(
                "At least one upstream measurement or analysis must be provided!"
            )
        for meas in measurements:
            if not isinstance(meas, Measurement):
                raise TypeError(
                    "All measurements must be of type `labgraph.nodes.Measurement`!"
                )
            meas.add_downstream(self)
            self.add_upstream(meas)

        for analysis in upstream_analyses:
            if not isinstance(analysis, Analysis):
                raise TypeError(
                    "All analyses must be of type `labgraph.nodes.Analysis`!"
                )
            analysis.add_downstream(self)
            self.add_upstream(analysis)
        self.analysismethod_id = analysis_method.id
        self.__analysis_method = analysis_method

        self.__measurements = measurements
        self.__upstream_analyses = upstream_analyses
        self._user_fields = user_fields

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

    @classmethod
    def from_dict(cls, entry: dict) -> "Analysis":
        from labgraph.views import AnalysisMethodView, MeasurementView, AnalysisView

        method = AnalysisMethodView().get(id=entry.pop("analysismethod_id"))
        _id = entry.pop("_id", None)
        version_history = entry.pop("version_history", [])

        entry.pop("created_at", None)
        entry.pop("updated_at", None)
        upstream = entry.pop("upstream")
        downstream = entry.pop("downstream")

        mv = MeasurementView()
        measurements = [
            mv.get(id=meas["node_id"])
            for meas in upstream
            if meas["node_type"] == "Measurement"
        ]
        av = AnalysisView()
        upstream_analyses = [
            av.get(id=ana["node_id"])
            for ana in upstream
            if ana["node_type"] == "Analysis"
        ]
        obj = cls(
            measurements=measurements,
            upstream_analyses=upstream_analyses,
            analysis_method=method,
            **entry,
        )
        if _id is not None:
            obj._id = _id
        for us in upstream:
            obj.upstream.append(us)
        for ds in downstream:
            obj.downstream.append(ds)
        obj._version_history = version_history

        return obj
