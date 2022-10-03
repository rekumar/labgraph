from bson import ObjectId
from datetime import datetime
from typing import cast, List, Dict
from alab_data.utils.data_objects import get_collection
from alab_data.data.nodes import BaseObject


class NotFoundInDatabaseError(ValueError):
    """Raised when a requested entry is not found in the database"""

    pass


## CRUD = Create Update Retrieve Delete
class BaseView:
    """
    Basic view to add, get, and remove entries from the database collections.
    """

    def __init__(
        self, collection: str, entry_class: type, allow_duplicate_names: bool = True
    ):
        self._collection = get_collection(collection)
        self._entry_class = entry_class
        self.allow_duplicate_names = allow_duplicate_names

    def add(self, entry, pass_if_already_in_db: bool = False) -> ObjectId:
        # TODO type check material. maybe this is done within Material class idk
        if not isinstance(entry, self._entry_class):
            raise ValueError(f"Entry must be of type {self._entry_class.__name__}")

        found_in_db = False
        try:
            self.get(id=entry.id)
            found_in_db = True
        except NotFoundInDatabaseError:
            pass
        if not self.allow_duplicate_names and not found_in_db:
            try:
                self.get_by_name(name=entry.name)
            except NotFoundInDatabaseError:
                pass  # entry is not in db, we can proceed to add it
        if found_in_db:
            if pass_if_already_in_db:
                return
            else:
                raise ValueError(
                    f"{self._entry_class.__name__} (name={entry.name}, id={entry.id}) already exists in the database!"
                )

        result = self._collection.insert_one(
            {
                **entry.to_dict(),
                "created_at": datetime.now(),
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

    def _entry_to_object(self, entry: dict):
        id = entry.pop("_id")
        entry.pop("created_at")

        is_dag_node = "upstream" in entry
        if is_dag_node:
            us = entry.pop("upstream")
            ds = entry.pop("downstream")

        obj = self._entry_class(**entry)
        obj._id = id

        if is_dag_node:
            obj.upstream = us
            obj.downstream = ds
        return obj
