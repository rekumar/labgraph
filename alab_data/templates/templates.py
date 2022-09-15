from bson import ObjectId
from typing import Dict, List, Union
from dataclasses import dataclass, field


@dataclass
class BaseAttribute:
    name: str
    dtype: type


@dataclass
class BaseParameter:
    name: str
    value: Union[str, int, float, bool]
    units: str
    dtype: type = field(init=False)

    def __post_init__(self):
        self.dtype = type(self.value)

    def to_dict_entry(self):
        return {
            self.name: {
                "value": self.value,
                "units": self.units,
                "dtype": self.dtype.__name__,
            }
        }


@dataclass
class BaseData:
    name: str
    dims: List[str]
    n_dims: int = field(init=False)
    values: List[Union[List[Union[float, int]], Union[float, int]]]

    def __post_init__(self):
        self.n_dims = len(self.dims)


class BaseTemplate:
    def __init__(
        self, name: str, type: str, required_parameters: List[BaseAttribute] = None
    ):
        self.name = name
        self.type = type
        if required_parameters is None:
            self.required_parameters = []
        else:
            self.required_parameters = required_parameters

    def add_required_attribute(self, name: str, dtype: type):
        parameter = BaseAttribute(name, dtype)
        if any([parameter.name == p.name for p in self.required_parameters]):
            raise ValueError(
                f"Parameter by name {parameter.name} already exists in template {self.name}"
            )
        self.required_parameters.append(parameter)

    @classmethod
    def load(cls, name: str) -> "BaseTemplate":
        """Load the template from the database

        Args:
            name (str): name of the template

        Returns:
            BaseTemplate: Template instance loaded from the database
        """
        # TODO pull the template from the db
        return cls(name=name)

    def add_to_db(cls):
        """Add this base template to the database. If the template already exists, error and do not overwrite."""
        pass

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        return self.to_dict()


class ActionTemplate(BaseTemplate):
    def __init__(self, name: str):
        super(ActionTemplate, self).__init__(
            name=name, type="action", required_parameters=None
        )
        self.add_required_attribute(name="input_materials", dtype=List[ObjectId])
        self.add_required_attribute(name="output_materials", dtype=List[ObjectId])
        self.add_required_attribute(
            name="actors", dtype=List[ObjectId]
        )  # TODO this should reference the hardware that performed the action
        # self.add_required_parameter(name="ULSA_action", dtype=str)


class MaterialTemplate(BaseTemplate):
    def __init__(self, name: str):
        super(MaterialTemplate, self).__init__(
            name=name, type="material", required_parameters=None
        )
        self.add_required_attribute(name="material_string", dtype=str)
        self.add_required_attribute(name="material_formula", dtype=str)
        self.add_required_attribute(
            name="composition",
            dtype=Dict[str, Union[str, float, Dict[str, float]]],
        )  # TODO this should be type checking for a composition object
        self.add_required_attribute(name="parent_action", dtype=ObjectId)


class MeasurementTemplate(BaseTemplate):
    def __init__(self, name: str):
        super(MeasurementTemplate, self).__init__(
            name=name, type="measurement", required_parameters=None
        )
        self.add_required_attribute(name="input_material", dtype=ObjectId)
        self.add_required_attribute(name="actors", dtype=List[ObjectId])
        self.add_required_attribute(name="parameters", dtype=Dict[str, BaseParameter])
        self.add_required_attribute(name="data", dtype=List[BaseData])


class AnalysisTemplate(BaseTemplate):
    def __init__(self, name: str):
        super(AnalysisTemplate, self).__init__(
            name=name, type="analysis", required_parameters=None
        )
        self.add_required_attribute(name="input_measurements", dtype=List[ObjectId])
        self.add_required_attribute(
            name="method", dtype=ObjectId
        )  # TODO link to the analysis method. ie analysis program, ML model/version, etc.
        self.add_required_attribute(
            name="data", dtype=Dict[str, Union[List[float], str, float]]
        )  # TODO type check for data structures


### Actors and Methods
class ActorTemplate(BaseTemplate):
    def __init__(self, name: str):
        super(ActorTemplate, self).__init__(
            name=name, type="actor", required_parameters=None
        )
        self.add_required_attribute(name="name", dtype=str)
        self.add_required_attribute(name="description", dtype=str)


class MethodTemplate(BaseTemplate):
    def __init__(self, name: str):
        super(MethodTemplate, self).__init__(
            name=name, type="method", required_parameters=None
        )
        self.add_required_attribute(name="name", dtype=str)
        self.add_required_attribute(name="description", dtype=str)
