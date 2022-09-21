from multiprocessing.sharedctypes import Value
from bson import ObjectId
from datetime import datetime
from typing import cast
from alab_data.utils.data_objects import get_collection


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
        except ValueError:
            pass
        if not self.allow_duplicate_names and not found_in_db:
            try:
                self.get_by_name(name=entry.name)
                found_in_db = True
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

    def get_by_tags(self, tags: list):
        data = self._collection.find({"tags": {"$all": tags}})
        return [self._entry_to_object(entry) for entry in data]

    def get_by_name(self, name: str):
        data = self._collection.find_one({"name": name})
        if data is None:
            raise NotFoundInDatabaseError(
                f"Cannot find an {self._entry_class.__name__} with name: {name}"
            )
        return self._entry_to_object(data)

    def get(self, id: ObjectId):
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

    def _entry_to_object(self, entry: dict):
        id = entry.pop("_id")
        entry.pop("created_at")
        obj = self._entry_class(**entry)
        obj._id = id
        return obj


# class BaseCompositeView:
#     def __init__(self, base_collection: BaseView):
#         self._base_collection = base_collection

#     def get(self, id: ObjectId):
#         return self._base_collection.get(id=id)

#     def get_by_name(self, name: str):
#         return self._base_collection.get_by_name(name=name)

#     def get_by_tags(self, tags: list):
#         return self._base_collection.get_by_tags(tags=tags)

#     def add(self, entry, pass_if_already_in_db: bool = False) -> ObjectId:
#         return self._base_collection.add(
#             entry=entry, pass_if_already_in_db=pass_if_already_in_db
#         )
