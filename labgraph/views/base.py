from abc import ABC, abstractmethod
from bson import ObjectId
from datetime import datetime
from typing import Literal, cast, List, Dict
from labgraph.utils.data_objects import get_collection
from labgraph.data.nodes import BaseObject
from labgraph.data.actors import BaseActor


class NotFoundInDatabaseError(ValueError):
    """Raised when a requested entry is not found in the database"""

    pass


class AlreadyInDatabaseError(ValueError):
    """Raised when a requested entry is already in the database"""

    pass


## CRUD = Create Update Retrieve Delete
class BaseView(ABC):
    """
    Basic view to add, get, and remove entries from the database collections.
    """

    def __init__(
        self, collection: str, entry_class: type, allow_duplicate_names: bool = True
    ):
        self._collection = get_collection(collection)
        self._entry_class = entry_class
        self.allow_duplicate_names = allow_duplicate_names

    def add(
        self, entry, if_already_in_db: Literal["raise", "skip", "update"] = "raise"
    ) -> ObjectId:
        # TODO type check material. maybe this is done within Material class idk
        if not isinstance(entry, self._entry_class):
            raise ValueError(f"Entry must be of type {self._entry_class.__name__}")

        found_in_db = False
        result = self._collection.count_documents({"_id": entry.id})
        found_in_db = result > 0
        if not self.allow_duplicate_names and not found_in_db:
            try:
                self.get_by_name(name=entry.name)
            except NotFoundInDatabaseError:
                pass  # entry is not in db, we can proceed to add it
        if found_in_db:
            if if_already_in_db == "skip":
                return entry.id
            elif if_already_in_db == "update":
                self.update(entry)
                return entry.id
            else:
                raise AlreadyInDatabaseError(
                    f"{self._entry_class.__name__} (name={entry.name}, id={entry.id}) already exists in the database!"
                )

        result = self._collection.insert_one(
            {
                **entry.to_dict(),
                "created_at": datetime.now().replace(
                    microsecond=0
                ),  # remove microseconds, they get lost in MongoDB anyways,
                "updated_at": datetime.now().replace(
                    microsecond=0
                ),  # remove microseconds, they get lost in MongoDB anyways,
            }
        )
        entry._id = result.inserted_id
        return cast(ObjectId, result.inserted_id)

    def get_by_tags(self, tags: list) -> List[BaseObject]:
        results = self._collection.find({"tags": {"$all": tags}})
        entries = [self._entry_to_object(entry) for entry in results]
        if len(entries) is None:
            raise NotFoundInDatabaseError(
                f"Cannot find a {self._entry_class.__name__} with tags: {tags}"
            )
        return entries

    def get_by_name(self, name: str) -> List[BaseObject]:
        results = self._collection.find({"name": name})
        entries = [self._entry_to_object(entry) for entry in results]
        if len(entries) == 0:
            raise NotFoundInDatabaseError(
                f"Cannot find an {self._entry_class.__name__} with name: {name}"
            )
        return entries

    def get(self, id: ObjectId) -> BaseObject:
        ## TODO
        data = self._collection.find_one({"_id": id})
        if data is None:
            raise NotFoundInDatabaseError(
                f"Cannot find an {self._entry_class.__name__} with id: {id}"
            )
        return self._entry_to_object(data)

    def remove(self, id: ObjectId):
        result = self._collection.delete_one({"_id": id})
        if result.deleted_count == 0:
            raise NotFoundInDatabaseError(
                f"Could not find a {self._entry_class.__name__} with id: {id}. Nothing was removed from the database."
            )

    def filter(
        self,
        filter_dict: Dict,
        datetime_min: datetime = None,
        datetime_max: datetime = None,
    ) -> List[BaseObject]:
        """Thin wrapper around pymongo find method, with an extra datetime filter

        Args:
            filter_dict (Dict): standard mongodb filter dictionary
            datetime_min (datetime, optional): entries from before this datetime will not be shown. Defaults to None.
            datetime_max (datetime, optional): entries from after this datetime will not be shown. Defaults to None.

        Returns:
            List[BaseObject]: List of Objects (nodes or samples) that match the filter
        """
        if datetime_min is not None:
            if "created_at" in filter_dict:
                filter_dict["created_at"]["$gte"] = datetime_max
            else:
                filter_dict["created_at"] = {"$gte": datetime_min}
        if datetime_max is not None:
            if "created_at" in filter_dict:
                filter_dict["created_at"]["$lte"] = datetime_max
            else:
                filter_dict["created_at"] = {"$lte": datetime_max}

        results = self._collection.find(filter_dict)
        return [self._entry_to_object(result) for result in results]

    def filter_one(
        self,
        filter_dict: Dict,
        datetime_min: datetime = None,
        datetime_max: datetime = None,
    ):
        """Return only the first entry from BaseView.filter. Useful if only one matching entry is expected."""
        return self.filter(filter_dict, datetime_min, datetime_max)[0]

    @abstractmethod
    def _entry_to_object(self, entry: dict):
        pass


class BaseNodeView(BaseView):
    def update(self, entry: BaseObject):
        """Updates an entry in the database. The previous entry will be placed in a `version_history` field of the entry.

        Args:
            entry (BaseObject): Node object to be updated

        Raises:
            TypeError: Node is of wrong type
            NotFoundInDatabaseError: Node does not exist in the database
            ValueError: Upstream nodes can only be added, not removed! Removing can break the graph.
            ValueError: Downstream nodes can only be added, not removed! Removing can break the graph.
        """
        if not isinstance(entry, self._entry_class):
            raise TypeError(f"Entry must be of type {self._entry_class.__name__}")

        old_entry = self._collection.find_one({"_id": entry.id})
        if old_entry is None:
            raise NotFoundInDatabaseError(
                f"Cannot update {self._entry_class.__name__} with id {entry.id} because it does not exist in the database."
            )

        new_entry = entry.to_dict()
        old_entry_for_comparison = {
            k: v
            for k, v in old_entry.items()
            if k not in ["version_history", "updated_at", "created_at"]
        }
        if new_entry == old_entry_for_comparison:
            return  # nothing to update

        if any(
            [
                old_upstream_node not in new_entry["upstream"]
                for old_upstream_node in old_entry["upstream"]
            ]
        ):
            raise ValueError("Cannot remove incoming edges from an existing node!")
        if any(
            [
                old_downstream_node not in new_entry["downstream"]
                for old_downstream_node in old_entry["downstream"]
            ]
        ):
            raise ValueError("Cannot remove outgoing edges from an existing node!")

        # If we are only connecting new nodes, we won't consider this a version update. Will instead update the current version in place.

        only_adding_nodes = True
        for key in new_entry:
            if key in ["upstream", "downstream"]:
                continue
            if key not in old_entry:
                only_adding_nodes = False
                break
            if new_entry[key] != old_entry[key]:
                only_adding_nodes = False
                break

        if only_adding_nodes:
            # no need for version history if we are only adding nodes
            self._collection.update_one(
                {"_id": entry.id},
                {
                    "$set": {
                        "upstream": new_entry["upstream"],
                        "downstream": new_entry["downstream"],
                        "updated_at": datetime.now().replace(
                            microsecond=0
                        ),  # remove microseconds, they get lost in MongoDB anyways,
                    }
                },
            )
        else:
            # if other things are changing, lets keep a version history
            new_entry["created_at"] = old_entry["created_at"]
            new_entry["updated_at"] = (
                datetime.now().replace(microsecond=0),
            )  # remove microseconds, they get lost in MongoDB anyways
            new_entry["version_history"] = old_entry.get("version_history", [])
            old_entry.pop("_id", None)
            old_entry.pop("version_history", None)
            new_entry["version_history"].append(old_entry)
            self._collection.replace_one({"_id": entry.id}, new_entry)

    def remove(self, id: ObjectId):
        raise NotImplementedError(
            "Node removal is not yet supported. Working on rules to ensure graph integrity upon node removal!"
        )


class BaseActorView(BaseView):
    def update(self, entry: BaseActor):
        if not isinstance(entry, BaseActor):
            raise TypeError(f"Entry must be of type {BaseActor.__name__}")

        old_entry = self._collection.find_one({"_id": entry.id})
        if old_entry is None:
            raise NotFoundInDatabaseError(
                f"Cannot update {self._entry_class.__name__} with id {entry.id} because it does not exist in the database."
            )

        old_version = max([v["version"] for v in old_entry["version_history"]])

        if old_version > entry.version:
            raise ValueError(
                "Cannot update! The current database entry is ahead (version {old.version} of the version you want to update to {entry.version}!"
            )

        # all remaining changes can be made without breaking the graph.
        new_entry = entry.to_dict()
        new_entry["created_at"] = old_entry["created_at"]
        new_entry["updated_at"] = (
            datetime.now().replace(microsecond=0),
        )  # remove microseconds, they get lost in MongoDB anyways
        self._collection.replace_one({"_id": entry.id}, new_entry)

    def _entry_to_object(self, entry: dict):
        id = entry.pop("_id")
        entry.pop("created_at")
        entry.pop("updated_at")
        entry.pop("version")
        version_history = entry.pop("version_history", None)

        obj = self._entry_class(**entry)
        obj._id = id
        obj._version_history = version_history

        return obj

    def remove(self, id: ObjectId):
        raise NotImplementedError(
            "Actor removal is not yet supported. Working on rules to ensure graph integrity upon actor removal!"
        )
