from typing import cast
from alab_data.utils.data_objects import get_collection
from alab_data import Analysis
from bson import ObjectId
from datetime import datetime


## CRUD = Create Update Retrieve Delete
class AnalysisView:
    """
    Experiment view manages the experiment status, which is a collection of tasks and samples
    """

    def __init__(self):
        self._collection = get_collection("analyses")

    def add(self, analysis: Analysis) -> ObjectId:
        # TODO type check material. maybe this is done within Material class idk
        if analysis.in_database:
            raise ValueError(
                f"Analysis {analysis.name} already exists in the database!"
            )
        result = self._collection.insert_one(
            {
                **analysis.to_dict(),
                "created_at": datetime.now(),
            }
        )
        return cast(ObjectId, result.inserted_id)

    def get(self, id: ObjectId) -> Analysis:
        data = self._collection.find_one({"_id": id})
        if data is None:
            raise ValueError(f"Cannot find an Analysis with id: {id}")
        analysis = Analysis(**data)
        analysis.id = id
        return analysis

    def remove(self, id: ObjectId):
        result = self._collection.delete_one({"_id": id})
        if result.deleted_count == 0:
            raise ValueError(
                f"Could not find a Material with id: {id}. Nothing was removed from the database."
            )
