from abc import abstractmethod
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
        **user_fields,
    ):
        self.name = name
        self.description = description

        if tags is None:
            self.tags = []
        else:
            self.tags = tags
        self._user_fields = user_fields

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

        user_fields = d.pop("_user_fields")
        for field_name in user_fields:
            if field_name in d:
                raise ValueError(
                    f"Parameter name {field_name} already exists as a default key of an {self.__class__.__name__}. Please rename this parameter and try again."
                )
        d.update(user_fields)
        return d

    @classmethod
    def from_dict(cls, entry: Dict[str, Any]):
        _id = entry.pop("_id", None)
        entry.pop("created_at", None)
        entry.pop("updated_at", None)
        entry.pop("version", None)
        version_history = entry.pop("version_history", None)

        obj = cls(**entry)
        if _id is not None:
            obj._id = _id
        obj._version_history = version_history

        return obj

    # @classmethod
    # @abstractmethod
    # def from_dict(cls, entry: Dict[str, Any]):
    #     raise NotImplementedError()

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

    @classmethod
    def __get_view(cls):
        from labgraph.views import ActorView, AnalysisMethodView

        VIEWS = {
            "Actor": ActorView,
            "AnalysisMethod": AnalysisMethodView,
        }
        return VIEWS[cls.__name__]()

    @classmethod
    def get_by_name(cls, name: str) -> "BaseActor":
        """Get an Actor or AnalysisMethod by name

        Args:
            name (str): Name of the actor or analysis method

        Returns:
            BaseActor: Actor or AnalysisMethod object
        """

        view = cls.__get_view()
        return view.get_by_name(name)[0]

    @classmethod
    def get_by_tags(cls, tags: List[str]) -> List["BaseActor"]:
        """Get an Actor or AnalysisMethod by tags

        Args:
            tags (List[str]): Tags of the actor or analysis method

        Returns:
            List[BaseActor]: List of Actor or AnalysisMethod objects
        """

        view = cls.__get_view()
        return view.get_by_tags(tags)

    @classmethod
    def filter(
        cls,
        filter_dict: dict,
        datetime_min: datetime = None,
        datetime_max: datetime = None,
    ) -> List["BaseActor"]:
        """Thin wrapper around pymongo find method, with an extra datetime filter.

        Args:
            filter_dict (Dict): standard mongodb filter dictionary.
            datetime_min (datetime, optional): entries from before this datetime will not be shown. Defaults to None.
            datetime_max (datetime, optional): entries from after this datetime will not be shown. Defaults to None.

        Returns:
            List[BaseActor]: List of Actors/AnalysisMethods that match the filter
        """
        view = cls.__get_view()
        return view.filter(filter_dict, datetime_min, datetime_max)

    @classmethod
    def filter_one(
        cls,
        filter_dict: dict,
        datetime_min: datetime = None,
        datetime_max: datetime = None,
    ) -> "BaseActor":
        """Thin wrapper around pymongo find_one method, with an extra datetime filter.

        Args:
            filter_dict (Dict): standard mongodb filter dictionary.
            datetime_min (datetime, optional): entries from before this datetime will not be shown. Defaults to None.
            datetime_max (datetime, optional): entries from after this datetime will not be shown. Defaults to None.

        Returns:
            BaseActor: Actor/AnalysisMethod that matches the filter
        """
        view = cls.__get_view()
        return view.filter_one(filter_dict, datetime_min, datetime_max)

    def save(self):
        view = self.__get_view()
        view.add(entry=self, if_already_in_db="update")

    def __getitem__(self, key: str):
        return self._user_fields[key]

    def __setitem__(self, key: str, value: Any):
        self._user_fields[key] = value

    def keys(self):
        return list(self._user_fields.keys())


class Actor(BaseActor):
    """An experimental actor (hardware, system, or lab facility) that can perform synthesis Action's or Measurement's"""

    def __init__(
        self, name: str, description: str, tags: List[str] = None, **user_fields
    ):
        super().__init__(name=name, description=description, tags=tags, **user_fields)


class AnalysisMethod(BaseActor):
    """A method to analyze data contained in one or more Measurement's to yield features of the measurement"""

    def __init__(
        self, name: str, description: str, tags: List[str] = None, **user_fields
    ):
        super().__init__(name=name, description=description, tags=tags, **user_fields)
