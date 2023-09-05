import datetime
from bson import ObjectId, BSON
from typing import Any, Dict, List, Optional, Union, Literal

from labgraph.errors import AlreadyInDatabaseError, NotFoundInDatabaseError

from .actors import Actor
from abc import ABC, abstractmethod
import re


class InvalidNodeDefinition(Exception):
    """Something is wrong with the node definition."""


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
            value = {
                "node_type": value.__class__.__name__,
                "node_id": value._id,
            }
        if isinstance(value, dict):
            if not all([k in value for k in ["node_type", "node_id"]]):
                raise ValueError(
                    "Invalid node entry. Dicts appended to NodeList must have keys 'node_type' and 'node_id'"
                )
            entry = {
                "node_type": value["node_type"],
                "node_id": value["node_id"],
            }
            if entry not in self:
                super().append(entry)
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
        labgraph_node_type: Literal[
            "Material", "Measurement", "Analysis", "Action"
        ] = None,
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
        self._contents = {}
        self._created_at = None  # time of creation within the database
        self._updated_at = None  # time of last update within the database

        if labgraph_node_type not in [
            "Material",
            "Measurement",
            "Analysis",
            "Action",
        ]:
            raise ValueError(
                "labgraph_node_type must be one of 'Material', 'Measurement', 'Analysis', or 'Action'"
            )

        self.__labgraph_node_type = labgraph_node_type

    def add_upstream(self, upstream: "BaseNode"):
        if not isinstance(upstream, BaseNode):
            raise TypeError("Upstream nodes must be a BaseObject")

        new_entry = {"node_type": upstream.labgraph_node_type, "node_id": upstream._id}
        if new_entry not in self.upstream:
            self.upstream.append(new_entry)

    def add_downstream(self, downstream: "BaseNode"):
        if not isinstance(downstream, BaseNode):
            raise TypeError("Upstream nodes must be a BaseObject")
        new_entry = {
            "node_type": downstream.labgraph_node_type,
            "node_id": downstream._id,
        }
        if new_entry not in self.downstream:
            self.downstream.append(new_entry)

    def to_dict(self):
        # hidden_property_mangle_prefix = r"_\w*__\w*"  # matches __property mangle prefix
        full_dict = {
            k: v
            for k, v in self.__dict__.items()
            # if not re.match(hidden_property_mangle_prefix, k)
            if not k.startswith("_")
        }  # dont include underscored class attributes

        # full_dict.pop("_version_history", None)
        # contents = full_dict.pop("_contents", {})

        return_dict = {
            "_id": self._id,  # only underscored value we need
        }

        for key in [
            "name",
            "tags",
            "upstream",
            "downstream",
            "version_history",
            "actor_id",
            "ingredients",
        ]:
            if key in full_dict:
                return_dict[key] = full_dict[key]

        for key in self._contents:
            if key in return_dict:
                raise ValueError(
                    f"User field {key} in node {self.name} of type {self.__class__} conflicts with default node attribute {key} -- please rename the parameter!"
                )
        return_dict["contents"] = self._contents
        # return_dict.update(self._contents)

        return return_dict

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
        except Exception:
            return False

    @abstractmethod
    def raise_if_invalid(self):
        """method to validate the object. Necessary before adding to database. If node is invalid, this method should raise an InvalidNodeDefinition exception."""
        raise NotImplementedError

    @property
    def id(self):
        return self._id

    @property
    def version_history(self):
        return self._version_history

    @property
    def labgraph_node_type(self):
        return self.__labgraph_node_type

    def __hash__(self):
        return hash(self.name + str(self.id))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.id == self.id

    def __repr__(self):
        return f"<{self.labgraph_node_type}: {self.name}>"

    def save(self):
        """Saves the node to the database."""
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
        return self._contents[key]

    def __setitem__(self, key: str, value: Any):
        self._contents[key] = value

    def keys(self):
        return list(self._contents.keys())

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

    def exists_in_database(self) -> bool:
        """Checks if the node exists in the database.

        Returns:
            bool: True if the node exists in the database.
        """
        view = self.__get_view()
        return view._exists(self.id)

    @property
    def created_at(self):
        if self._created_at is None:
            return "This node has not been saved to the database yet."
        return self._created_at

    @property
    def updated_at(self):
        if self._updated_at is None:
            return "This node has not been saved to the database yet."
        return self._updated_at

    def raise_if_invalid(self):
        """method to validate the object. Necessary before adding to database. If node is invalid, this method should raise an InvalidNodeDefinition exception."""
        return 
## Materials
class Material(BaseNode):
    """Class to define a Material node. These nodes capture information about a material in a given state. Each Material is created by an Action. Measurements can act upon a Material to yield raw characterization data."""

    def __init__(
        self,
        name: str,
        tags: Optional[Union[List[str], None]] = None,
        **contents,
    ):
        """Initialize a Material node. This creates the node in memory -- it is not added to the database yet!

        Args:
            name (str): Name of this Material. This is purely for human readability, and does not need to be unique.
            tags (Optional[Union[List[str], None]], optional): A list of tags to catalog this Material. If None (default), no tags will be applied. Tags can be an easy way to query nodes.
            **contents: Any additional values to be stored in the node. These will be stored as key-value pairs in the node entry in the database. While these values are not used by the database, they can be useful for storing additional information about the node according to user needs. All values within these fields must be BSON-serializable (e.g. no numpy arrays, etc.) such that they can be stored using MongoDB.
        """
        super(Material, self).__init__(
            name=name, tags=tags, labgraph_node_type="Material"
        )
        self._contents = contents

    def raise_if_invalid(self):
        for node in self.upstream:
            if node["node_type"] != "Action":
                raise InvalidNodeDefinition(
                    f"{self} has upstream node {node} of type {node['node_type']}. All upstream nodes must be of type Action."
                )
        for node in self.downstream:
            if node["node_type"] not in ["Action", "Measurement"]:
                raise InvalidNodeDefinition(
                    f"{self} has downstream node {node} of type {node['node_type']}. All downstream nodes must be of type Action or Measurement."
                )

    @classmethod
    def from_dict(cls, entry: dict) -> "Material":
        _id = entry.pop("_id", None)
        version_history = entry.pop("version_history", [])
        created_at = entry.pop("created_at", None)
        updated_at = entry.pop("updated_at", None)
        contents = entry.pop("contents", {})

        us = entry.pop("upstream")
        ds = entry.pop("downstream")

        obj = cls(**entry, **contents)
        if _id is not None:
            obj._id = _id
        obj._version_history = version_history
        obj._created_at = entry.pop("created_at", None)
        obj._updated_at = entry.pop("updated_at", None)

        for us_ in us:
            obj.upstream.append(us_)
        for ds_ in ds:
            obj.downstream.append(ds_)

        obj._version_history = version_history
        obj._updated_at = updated_at
        obj._created_at = created_at
        return obj


## Actions
class Ingredient:
    def __init__(
        self,
        material: Material,
        amount: float,
        unit: str,
        name: str = None,
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
        self.__material = material
        self.material_id = material.id
        self.amount = amount
        self.unit = unit

    @property
    def material(self) -> Material:
        if not self.__material:
            try:
                self.__material = Material.get(self.material_id)
            except:
                raise NotFoundInDatabaseError(
                    f"Could not retrieve material for {str(self)} from database! Upstream Material node was not found in the database. Most likely you rebuilt this Ingredient using Ingredient.from_dict() for an Ingredient that was not yet saved to the database."
                )
        return self.__material

    def to_dict(self):
        d = self.__dict__.copy()
        d = {k: v for k, v in d.items() if not k.startswith("_")}

        return d

    @classmethod
    def from_dict(cls, d: dict):
        dummy_material = Material(name="this is ugly and tricky but whatever")

        ingredient = cls(
            material=dummy_material,
            amount=d["amount"],
            unit=d["unit"],
            name=d["name"],
        )

        ingredient.__material = None
        ingredient.material_id = d["material_id"]
        return ingredient

    def __repr__(self):
        s = f"<Ingredient: {self.name} ({self.amount} {self.unit} of {self.material})>"
        return s


class WholeIngredient(Ingredient):
    def __init__(self, material: Material, name: str = None):
        """Shortcut for when 100% of a material is consumed by an action. This is common for actions performed on intermediate materials.

        Args:
            material (Material): Material node described by this ingredient.
            name (str, optional): Name of this ingredient. This differs from the Material name. For example, a Material "cheese" may be an Ingredient named "topping" in a "Make Pizza" action. Defaults to None.
        """
        super(WholeIngredient, self).__init__(
            material=material, amount=100, unit="percent", name=name
        )


class UnspecifiedAmountIngredient(Ingredient):
    def __init__(self, material: Material, name: str = None):
        """Shortcut for when an unknown amount of material is consumed by an action. This is common for actions performed on intermediate materials, or when samples are defined before the amount of material is known.

        Args:
            material (Material): Material node described by this ingredient.
            name (str, optional): Name of this ingredient. This differs from the Material name. For example, a Material "cheese" may be an Ingredient named "topping" in a "Make Pizza" action. Defaults to None.
        """
        super(UnspecifiedAmountIngredient, self).__init__(
            material=material, amount=None, unit=None, name=name
        )


class BaseNodeWithActor(BaseNode):
    def __init__(
        self,
        name: str,
        actor: Union[Actor, List[Actor]],
        tags: Optional[List[str]] = None,
        labgraph_node_type: Optional[str] = None,
    ):
        """Generates an Action node. Actions create new Material(s), optionally using existing Material(s) in the form of Ingredient(s). Actions are the primary way to create new Material nodes in the database.

        Args:
            name (str): Name of the Action node.
            actor (Union[Actor, List[Actor]]): Actor(s) which perform this Action.
            tags (List[str], optional): List of string tags used to identify this Action node. Defaults to None.
        """
        super(BaseNodeWithActor, self).__init__(name=name, tags=tags, labgraph_node_type=labgraph_node_type)
        if isinstance(actor, Actor):
            actor = [actor]
        self.__actor = set()
        for a in actor:
            self.add_actor(actor=a)
        
    @property
    def actor(self):
        if len(self.__actor) == 0:
            return None
        return list(self.__actor)
    
    def add_actor(self, actor: Actor):
        if not isinstance(actor, Actor):
            raise TypeError(
                "The `actor` argument must be of type `labgraph.nodes.Actor`!"
            )
        self.__actor.add(actor)
        
    def remove_actor(self, actor: Actor):
        if not isinstance(actor, Actor):
            raise TypeError(
                "The `actor` argument must be of type `labgraph.nodes.Actor`!"
            )
        if actor not in self.__actor:
            raise ValueError(
                f"Cannot remove {actor} from {self}, as it is not in this node to begin with!"
            )
        self.__actor.remove(actor)
        
    @property
    def actor_id(self):
        return [a.id for a in self.__actor]

    def to_dict(self):
        d = super(BaseNodeWithActor, self).to_dict()
        d["actor_id"] = self.actor_id
        return d
    
    def raise_if_invalid(self):
        super().raise_if_invalid()

        if self.actor is None:
            raise InvalidNodeDefinition(
                f"{self} has no actor! You must add an actor to this type of node using either the `actor = ` argument in the constructor, or the `self.add_actor(actor= )` method after construction."
            )
        
class Action(BaseNodeWithActor):
    def __init__(
        self,
        name: str,
        actor: Union[Actor, List[Actor]],
        ingredients: List[Ingredient] = [],
        generated_materials: List[Material] = None,
        tags: List[str] = None,
        **contents,
    ):
        """Generates an Action node. Actions create new Material(s), optionally using existing Material(s) in the form of Ingredient(s). Actions are the primary way to create new Material nodes in the database.

        Args:
            name (str): Name of the Action node.
            actor (Union[Actor, List[Actor]]): Actor(s) which perform this Action.
            ingredients (List[Ingredient], optional): List of Ingredient objects, which describes a Material node with the amount of Material used in this Action. Defaults to [].
            generated_materials (List[Material], optional): Material Node(s) created by this Action. Defaults to None.
            tags (List[str], optional): List of string tags used to identify this Action node. Defaults to None.
        """
        super(Action, self).__init__(name=name, tags=tags, actor=actor, labgraph_node_type="Action")
        self._contents = contents
        self.ingredients = []
        self.__generated_materials = []
        for ingredient in ingredients or []:
            self.add_ingredient(ingredient)

        for material in generated_materials or []:
            self.add_generated_material(material)

    def add_ingredient(self, ingredient: Union[Ingredient, Material]):
        if isinstance(ingredient, Material):
            ingredient = UnspecifiedAmountIngredient(material=ingredient)
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
        if material in self.generated_materials:
            pass  # already added
        self.add_downstream(material)
        material.add_upstream(self)
        self.__generated_materials.append(material)

    @property
    def generated_materials(self):
        if len(self.__generated_materials) == 0 and len(self.downstream) > 0:
            """we must have built this Action from a database entry, so we need to populate the generated_materials list from the downstream nodes."""
            try:
                self.__generated_materials = [
                    Material.get(ds["node_id"]) for ds in self.downstream
                ]
            except:
                raise NotFoundInDatabaseError(
                    f"Could not retrieve generated materials for {str(self)} from database! Some or all downstream Material nodes were not found in the database. Most likely you rebuilt this Action using Action.from_dict() for an Action that was not yet saved to the database."
                )
        return self.__generated_materials

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

    def raise_if_invalid(self):
        super().raise_if_invalid()
        
        for node in self.upstream:
            if node["node_type"] != "Material":
                raise InvalidNodeDefinition(
                    f"{self} has upstream node {node} of type {node['node_type']}. All upstream nodes must be of type Material."
                )

        for node in self.downstream:
            if node["node_type"] not in ["Material", "Measurement"]:
                raise InvalidNodeDefinition(
                    f"{self} has downstream node {node} of type {node['node_type']}. All downstream nodes must be of type Material or Measurement."
                )
        if len(self.downstream) + len(self.upstream) == 0:
            raise InvalidNodeDefinition(
                f"{self} is not linked to any Materials. An Action must have at least one ingredient (incoming edge from material node) or generated material (outgoing edge to material node)!"
            )

    def to_dict(self) -> dict:
        d = super(Action, self).to_dict()
        d["ingredients"] = [i.to_dict() for i in self.ingredients]

        return d

    @classmethod
    def from_dict(cls, entry: dict) -> "Action":
        from labgraph.views import ActorView
        from labgraph.views import MaterialView

        actor = [
            ActorView().get(id=actor_id)
            for actor_id in entry.pop("actor_id")
        ]
        ingredients = [
            Ingredient.from_dict(this_ingredient)
            for this_ingredient in entry.pop("ingredients", [])
        ]
        _id = entry.pop("_id", None)
        version_history = entry.pop("version_history", [])
        created_at = entry.pop("created_at", None)
        updated_at = entry.pop("updated_at", None)
        upstream = entry.pop("upstream")
        downstream = entry.pop("downstream")
        contents = entry.pop("contents", {})
        obj = cls(
            actor=actor,
            **entry,
            **contents,
        )

        if _id:
            obj._id = _id

        # obj.upstream is a NodeList, not a normal list, so we need to append the upstream material manually
        for us in upstream:
            obj.upstream.append(us)
        for ds in downstream:
            obj.downstream.append(ds)
        obj._version_history = version_history
        obj._updated_at = updated_at
        obj._created_at = created_at
        obj.ingredients = ingredients
        return obj


## Measurements
class Measurement(BaseNodeWithActor):
    def __init__(
        self,
        name: str,
        material: Material = None,
        actor: Union[Actor, List[Actor]] = None,
        tags: List[str] = None,
        **contents,
    ):
        """A Measurement Node. This is a node that represents a measurement of a material by an actor.

        Args:
            name (str): Name of the measurement.
            material (Material): Material node upon which this Measurement is performed.
            actor (Union[Actor, List[Actor]]): Actor(s) which perform the measurement.
            tags (List[str], optional): List of string tags to identify this node. Defaults to None.

        Raises:
            TypeError: Invalid type for `material` argument.
        """
        super(Measurement, self).__init__(
            name=name, tags=tags, actor=actor, labgraph_node_type="Measurement"
        )
        self.__material = None
        if material:
            self.material = material
        self._contents = contents

    @property
    def material(self):
        if not self.__material and len(self.upstream) > 0:
            """we must have built this Measurement from a database entry, so we need to populate the material from the upstream nodes."""
            try:
                self.__material = Material.get(self.upstream[0]["node_id"])
            except:
                raise NotFoundInDatabaseError(
                    f"Could not retrieve material for {str(self)} from database! Upstream Material node was not found in the database. Most likely you rebuilt this Measurement using Measurement.from_dict() for a Measurement that was not yet saved to the database."
                )
        return self.__material

    @material.setter
    def material(self, material: Material):
        if not isinstance(material, Material):
            raise TypeError(
                "The `material` argument to a Measurement must be of type `labgraph.nodes.Material`!"
            )
        if self.__material is not None:
            raise ValueError(
                f"This Measurement is already linked to {str(self.__material)}! A Measurement can only be performed on one Material. If you want to perform a measurement on multiple Materials, you must create multiple Measurements."
            )
        self.__material = material
        self.material.add_downstream(self)
        self.add_upstream(material)

    def raise_if_invalid(self):
        super().raise_if_invalid()
        
        for node in self.upstream:
            if node["node_type"] != "Material":
                raise InvalidNodeDefinition(
                    f"{self} has upstream node {node} of type {node['node_type']}. All upstream nodes must be of type Material."
                )

        if len(self.upstream) != 1:
            raise InvalidNodeDefinition(
                f"{self} must have an input Material! Set this with the `material` argument to the constructor, or after the fact `using self.material = Material(...)`."
            )

        for node in self.downstream:
            if node["node_type"] != "Analysis":
                raise InvalidNodeDefinition(
                    f"{self} has downstream node {node} of type {node['node_type']}. All downstream nodes must be of type Analysis."
                )

    @classmethod
    def from_dict(cls, entry: dict) -> "Measurement":
        from labgraph.views import ActorView
        from labgraph.views import MaterialView

        actor = [
            ActorView().get(id=actor_id)
            for actor_id in entry.pop("actor_id")
        ]
        _id = entry.pop("_id", None)
        version_history = entry.pop("version_history", [])
        created_at = entry.pop("created_at", None)
        updated_at = entry.pop("updated_at", None)
        contents = entry.pop("contents", {})
        upstream = entry.pop("upstream")
        downstream = entry.pop("downstream")

        obj = cls(actor=actor, **entry, **contents)

        if _id is not None:
            obj._id = _id

        # obj.upstream is a NodeList, not a normal list, so we need to append the upstream material manually
        for us in upstream:
            obj.upstream.append(us)
        for ds in downstream:
            obj.downstream.append(ds)
        obj._version_history = version_history
        obj._updated_at = updated_at
        obj._created_at = created_at

        return obj


## Analyses
class Analysis(BaseNodeWithActor):
    def __init__(
        self,
        name: str,
        actor: Union[Actor, List[Actor]] = None,
        measurements: List[Measurement] = None,
        upstream_analyses: List["Analysis"] = None,
        tags: List[str] = None,
        **contents,
    ):
        """Creates an Analysis node. This node represents data processing from upstream Measurement(s) and/or Analysis/es node(s). For example, a "Density" Analysis may accept "Mass" and "Volume" measurements to compute density.

        Args:
            name (str): Name of the Analysis node.
            actor (Union[Actor, List[Actor]]): Actor(s) that perform this analysis.
            measurements (List[Measurement]): Measurements, if any, on which this Analysis is based. Defaults to None. At least one upstream measurement or analysis must be provided.
            upstream_analyses (List[Analysis]): Analysis node(s), if any, on which this Analysis is based. Defaults to None. At least one upstream measurement or analysis must be provided.
            tags (List[str], optional): List of string tags. Defaults to None.

        Raises:
            TypeError: Invalid node type passed to `measurements` or `analyses` arguments.
        """
        super(Analysis, self).__init__(
            name=name, tags=tags, actor=actor, labgraph_node_type="Analysis"
        )
        self.__measurements = []
        self.__upstream_analyses = []
        self._contents = contents

        for meas in measurements or []:
            self.add_measurement(meas)

        for analysis in upstream_analyses or []:
            self.add_upstream_analysis(analysis)

    def add_measurement(self, measurement: Measurement):
        if not isinstance(measurement, Measurement):
            raise TypeError(
                "All measurements must be of type `labgraph.data.nodes.Measurement`!"
            )
        measurement.add_downstream(self)
        self.add_upstream(measurement)
        self.__measurements.append(measurement)

    def add_upstream_analysis(self, analysis: "Analysis"):
        if not isinstance(analysis, Analysis):
            raise TypeError(
                "All analyses must be of type `labgraph.data.nodes.Analysis`!"
            )
        analysis.add_downstream(self)
        self.add_upstream(analysis)
        self.__upstream_analyses.append(analysis)

    def add_measurement(self, measurement: Measurement):
        if not isinstance(measurement, Measurement):
            raise TypeError(
                "All measurements must be of type `labgraph.data.nodes.Measurement`!"
            )
        measurement.add_downstream(self)
        self.add_upstream(measurement)
        self.__measurements.append(measurement)

    def add_upstream_analysis(self, analysis: "Analysis"):
        if not isinstance(analysis, Analysis):
            raise TypeError(
                "All analyses must be of type `labgraph.data.nodes.Analysis`!"
            )
        analysis.add_downstream(self)
        self.add_upstream(analysis)
        self.__upstream_analyses.append(analysis)

    @property
    def measurements(self):
        if len(self.__measurements) == 0 and len(self.upstream) > 0:
            """we must have built this Analysis from a database entry, so we need to populate the measurements from the upstream nodes."""
            try:
                self.__measurements = [
                    Measurement.get(ms["node_id"])
                    for ms in self.upstream
                    if ms["node_type"] == "Measurement"
                ]
            except:
                raise NotFoundInDatabaseError(
                    f"Could not retrieve measurements for {str(self)} from database! Some or all upstream Measurement nodes were not found in the database. Most likely you rebuilt this Analysis using Analysis.from_dict() for an Analysis that was not yet saved to the database."
                )
        return self.__measurements

    @property
    def upstream_analyses(self):
        if len(self.__upstream_analyses) == 0 and len(self.upstream) > 0:
            """we must have built this Analysis from a database entry, so we need to populate the upstream_analyses from the upstream nodes."""
            try:
                self.__upstream_analyses = [
                    Analysis.get(ana["node_id"])
                    for ana in self.upstream
                    if ana["node_type"] == "Analysis"
                ]
            except:
                raise NotFoundInDatabaseError(
                    f"Could not retrieve upstream analyses for {str(self)} from database! Some or all upstream Analysis nodes were not found in the database. Most likely you rebuilt this Analysis using Analysis.from_dict() for an Analysis that was not yet saved to the database."
                )
        return self.__upstream_analyses

    def raise_if_invalid(self):
        super().raise_if_invalid()

        for node in self.upstream:
            if node["node_type"] not in ["Measurement", "Analysis"]:
                raise InvalidNodeDefinition(
                    f"{self} has upstream node {node} of type {node['node_type']}. All upstream nodes must be of type Measurement."
                )

        # Allow analyses to have no upstream nodes, like if training an ML model or running a simulation to feed other analyses. 
        # if len(self.upstream) == 0:
        #     raise InvalidNodeDefinition(
        #         f"{self} is not linked to any Measurements or Analyses. An Analysis must have at least one upstream Measurement or Analysis!"
        #     )

        for node in self.downstream:
            if node["node_type"] != "Analysis":
                raise InvalidNodeDefinition(
                    f"{self} has downstream node {node} of type {node['node_type']}. All downstream nodes must be of type Analysis."
                )

    @classmethod
    def from_dict(cls, entry: dict) -> "Analysis":
        from labgraph.views import ActorView

        actor = [
            ActorView().get(id=actor_id)
            for actor_id in entry.pop("actor_id")
        ]
        _id = entry.pop("_id", None)
        version_history = entry.pop("version_history", [])

        created_at = entry.pop("created_at", None)
        updated_at = entry.pop("updated_at", None)
        upstream = entry.pop("upstream")
        downstream = entry.pop("downstream")
        contents = entry.pop("contents", {})

        obj = cls(
            actor=actor,
            **entry,
            **contents,
        )
        if _id is not None:
            obj._id = _id

        # obj.upstream is a NodeList, not a normal list, so we need to append the upstream material manually
        for us in upstream:
            obj.upstream.append(us)
        for ds in downstream:
            obj.downstream.append(ds)
        obj._version_history = version_history
        obj._updated_at = updated_at
        obj._created_at = created_at

        return obj
