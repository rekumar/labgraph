from bson import ObjectId


class BaseObject:
    def __init__(
        self,
        name: str,
    ):
        self.name = name
        self.__id = None

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        return self.to_dict()

    def __repr__(self):
        return str(self.to_dict())

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id: ObjectId):
        if self.__id is not None:
            raise Exception("Cannot overwrite existing id: {}".format(self.__id))
        self.__id = id

    @property
    def in_database(self):
        return self.id is not None


class Actor(BaseObject):
    """An experimental actor (hardware, system, or lab facility) that can perform synthesis Action's or Measurement's"""

    def __init__(self, name: str, description: str):
        super(Actor, self).__init__(name=name)
        self.description = description


class AnalysisMethod(BaseObject):
    """A method to analyze data contained in one or more Measurement's to yield features of the measurement"""

    def __init__(self, name: str, description: str):
        super(AnalysisMethod, self).__init__(name=name)
        self.description = description
        # TODO add required Measurement/data type to feed this analysis
