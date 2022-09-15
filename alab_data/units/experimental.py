from bson import ObjectId
from typing import List


class BaseObject:
    def __init__(
        self,
        name: str,
        upstream: List[ObjectId] = None,
        downstream: List[ObjectId] = None,
    ):
        self.name = name
        self.__id = None
        if upstream is None:
            self.upstream = []
        else:
            self.upstream = upstream
        if downstream is None:
            self.downstream = []
        else:
            self.downstream = downstream

    def add_upstream(self, upstream: ObjectId):
        self.upstream.append(upstream)

    def add_downstream(self, downstream: ObjectId):
        self.downstream.append(downstream)

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


class Material(BaseObject):
    def __init__(self, name: str, intermediate: bool = False):
        super(Material, self).__init__(name=name)
        self.intermediate = intermediate


class Action(BaseObject):
    def __init__(
        self,
        name: str,
        materials: List[Material] = [],
        generated_material_name: str = None,
        final_step: bool = False,
        **parameters
    ):
        super(Action, self).__init__(name=name)
        self.parameters = parameters
        self.materials = []
        if len(materials) > 0:
            for material in materials:
                self.add_upstream(material.id)
                material.add_downstream(self.id)
                self.materials.append(material.id)
        else:
            if generated_material_name is None:
                raise ValueError(
                    "If input material is not specified, the generated material name must be specified!"
                )
            self.materials = []

        if generated_material_name is None:
            generated_material_name = ""
            for material in materials:
                generated_material_name += material.name + "+"
            generated_material_name = generated_material_name[:-1] + " - " + name

        self.__generated_material = Material(
            name=generated_material_name, intermediate=not final_step
        )
        self.__generated_material.add_upstream(self.id)

    @property
    def generated_material(self):
        return self.__generated_material


class Measurement(BaseObject):
    def __init__(self, name: str, material: Material, **parameters):
        super(Measurement, self).__init__(name=name)
        self.material = material
        self.parameters = parameters

        self.material.add_downstream(self.id)
        self.add_upstream(material.id)


class Analysis(BaseObject):
    def __init__(self, name: str, measurement: Measurement, **parameters):
        super(Analysis, self).__init__(name=name)
        self.measurement = measurement
        self.parameters = parameters

        self.measurement.add_downstream(self.id)
        self.add_upstream(measurement.id)
