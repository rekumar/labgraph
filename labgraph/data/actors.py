from typing import List
from bson import ObjectId


class BaseObject:
    def __init__(self, name: str, tags: List[str] = None, **parameters):
        self.name = name
        self._id = ObjectId()
        if tags is None:
            self.tags = []
        else:
            self.tags = tags
        self.parameters = parameters

    def to_dict(self):
        d = self.__dict__
        parameters = d.pop("parameters")
        for param_name in parameters:
            if param_name in d:
                raise ValueError(
                    f"Parameter name {param_name} already exists as a default key of an {self.__class__.__name__}. Please rename this parameter and try again."
                )
        d.update(parameters)
        return d

    def to_json(self):
        return self.to_dict()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    @property
    def id(self):
        return self._id


class Actor(BaseObject):
    """An experimental actor (hardware, system, or lab facility) that can perform synthesis Action's or Measurement's"""

    def __init__(
        self, name: str, description: str, tags: List[str] = None, **parameters
    ):
        super(Actor, self).__init__(name=name, tags=tags, **parameters)
        self.description = description


class AnalysisMethod(BaseObject):
    """A method to analyze data contained in one or more Measurement's to yield features of the measurement"""

    def __init__(
        self, name: str, description: str, tags: List[str] = None, **parameters
    ):
        super(AnalysisMethod, self).__init__(name=name, tags=tags, **parameters)
        self.description = description
        # TODO add required Measurement/data type to feed this analysis
