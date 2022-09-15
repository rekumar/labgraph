from typing import cast
from alab_data.utils.data_objects import get_collection
from alab_data import Actor
from bson import ObjectId
from datetime import datetime


## CRUD = Create Update Retrieve Delete
class ActorView:
    """
    Collects all analysis actors that are have been used to build Analysis nodes from Measurement nodes.
    """

    def __init__(self):
        self._collection = get_collection("actors")

    def add(self, actor: Actor) -> ObjectId:
        # TODO type check actor. maybe this is done within Material class idk
        if actor.in_database:
            raise ValueError(
                f"Analysis actor {actor.name} already exists in the database!"
            )
        result = self._collection.insert_one(
            {
                **actor.to_dict(),
                "created_at": datetime.now(),
            }
        )
        return cast(ObjectId, result.inserted_id)

    def get(self, id: ObjectId) -> Actor:
        actor_data = self._collection.find_one({"_id": id})
        if actor_data is None:
            raise ValueError(f"Cannot find an Actor with id: {id}")
        actor = Actor(**actor_data)
        actor.id = id
        return actor

    def remove(self, id: ObjectId):
        result = self._collection.delete_one({"_id": id})
        if result.deleted_count == 0:
            raise ValueError(
                f"Could not find an Actor with id: {id}. Nothing was removed from the database."
            )
