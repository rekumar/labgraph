from typing import cast
from alab_data.utils.data_objects import get_collection
from alab_data import AnalysisMethod
from bson import ObjectId
from datetime import datetime


## CRUD = Create Update Retrieve Delete
class AnalysisMethodView:
    """
    Collects all analysis methods that are have been used to build Analysis nodes from Measurement nodes.
    """

    def __init__(self):
        self._collection = get_collection("analysismethods")

    def add(self, method: AnalysisMethod) -> ObjectId:
        # TODO type check method. maybe this is done within Material class idk
        if method.in_database:
            raise ValueError(
                f"Analysis method {method.name} already exists in the database!"
            )
        result = self._collection.insert_one(
            {
                **method.to_dict(),
                "created_at": datetime.now(),
            }
        )
        return cast(ObjectId, result.inserted_id)

    def get(self, id: ObjectId) -> AnalysisMethod:
        method_data = self._collection.find_one({"_id": id})
        if method_data is None:
            raise ValueError(f"Cannot find an AnalysisMethod with id: {id}")
        method = AnalysisMethod(**method_data)
        method.id = id
        return method

    def remove(self, id: ObjectId):
        result = self._collection.delete_one({"_id": id})
        if result.deleted_count == 0:
            raise ValueError(
                f"Could not find an AnalysisMethod with id: {id}. Nothing was removed from the database."
            )
