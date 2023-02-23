from copy import deepcopy
import datetime
from typing import Any, Dict, List, Optional
from bson import ObjectId


class BaseActor:
    def __init__(
        self,
        name: str,
        description: str,
        tags: List[str] = None,
        **parameters,
    ):
        self.name = name
        self.description = description

        if tags is None:
            self.tags = []
        else:
            self.tags = tags
        self.parameters = parameters

        self._id = ObjectId()
        self._version_history = [
            {
                "version": 1,
                "description": "Initial version.",
                "version_date": datetime.datetime.now().replace(
                    microsecond=0
                ),  # remove microseconds, they get lost in MongoDB anyways
            }
        ]

    @property
    def id(self):
        return self._id

    @property
    def version_history(self):
        return self._version_history.copy()

    @property
    def version(self):
        return max([version["version"] for version in self.version_history])

    def to_dict(self):
        d = deepcopy(self.__dict__)
        d.pop("_version_history")
        d["version"] = self.version

        # in case we reformat version_history within the property down the line
        d["version_history"] = self.version_history

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
        return f"<{self.__class__.__name__}: {self.name} v{self.version}>"

    def new_version(self, description: str):
        """Increment the version of the actor and record a description of what changed in this version. This is used to track changes (instrument service, modification, update to analysis code, etc) to an actor/analysismethod over time.

        Note that this function only changes the actor locally. You need to call .update() in the database view to record this updated version to the database.

        Args:
            description (str): Description of the changes made to the actor in this version
        """

        self._version_history.append(
            {
                "version": self.version + 1,
                "description": description,
                "version_date": datetime.datetime.now().replace(
                    microsecond=0
                ),  # remove microseconds, they get lost in MongoDB anyways,
            }
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.id != other.id:
            return False
        if self.to_dict() != other.to_dict():
            raise ValueError(
                f"Objects have the same id but different attributes: {self.to_dict()} != {other.to_dict()}. Be careful, you have two different version of the same object!"
            )
        return True


class Actor(BaseActor):
    """An experimental actor (hardware, system, or lab facility) that can perform synthesis Action's or Measurement's"""

    def __init__(
        self, name: str, description: str, tags: List[str] = None, **parameters
    ):
        super().__init__(name=name, description=description, tags=tags, **parameters)

    @classmethod
    def get_by_name(cls, name: str) -> "Actor":
        """Get an actor by name

        Args:
            name (str): Name of the actor

        Returns:
            Actor: Actor object
        """
        from labgraph.views import ActorView

        return ActorView().get_by_name(name)[0]


class AnalysisMethod(BaseActor):
    """A method to analyze data contained in one or more Measurement's to yield features of the measurement"""

    def __init__(
        self, name: str, description: str, tags: List[str] = None, **parameters
    ):
        super().__init__(name=name, description=description, tags=tags, **parameters)

    @classmethod
    def get_by_name(cls, name: str) -> "AnalysisMethod":
        """Get an analysis method by name

        Args:
            name (str): Name of the analysis method

        Returns:
            AnalysisMethod: AnalysisMethod object
        """
        from labgraph.views import AnalysisMethodView

        return AnalysisMethodView().get_by_name(name)[0]
