from typing import List
from bson import ObjectId


class BaseObject:
    def __init__(self, name: str, tags: List[str] = None):
        self.name = name
        self._id = ObjectId()
        if tags is None:
            self.tags = []
        else:
            self.tags = tags

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        return self.to_dict()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    @property
    def id(self):
        return self._id


class Actor(BaseObject):
    """An experimental actor (hardware, system, or lab facility) that can perform synthesis Action's or Measurement's"""

    def __init__(self, name: str, description: str, tags: List[str] = None):
        super(Actor, self).__init__(name=name, tags=tags)
        self.description = description


class AnalysisMethod(BaseObject):
    """A method to analyze data contained in one or more Measurement's to yield features of the measurement"""

    def __init__(self, name: str, description: str, tags: List[str] = None):
        super(AnalysisMethod, self).__init__(name=name, tags=tags)
        self.description = description
        # TODO add required Measurement/data type to feed this analysis
