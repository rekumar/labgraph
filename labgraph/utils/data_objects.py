"""
A convenient wrapper for MongoClient. We can get a database object by calling ``get_collection`` function.
"""

from typing import Optional

import pymongo
from pymongo import collection, database

from .db_lock import MongoLock



class LabgraphDefaultMongoDB:
    client: Optional[pymongo.MongoClient] = None
    db: Optional[database.Database] = None
    db_lock: Optional[MongoLock] = None

    @classmethod
    def init(cls):
        from labgraph.utils import get_config

        db_config = get_config()["mongodb"]
        cls.client = pymongo.MongoClient(
            host=db_config.get("host", None),
            port=db_config.get("port", None),
            username=db_config.get("username", ""),
            password=db_config.get("password", ""),
        )
        cls.db = cls.client[db_config.get("db_name")]  # type: ignore # pylint: disable=unsubscriptable-object

    @classmethod
    def get_collection(cls, name: str) -> collection.Collection:
        """
        Get collection by name
        """
        if cls.client is None:
            cls.init()

        return cls.db[name]  # type: ignore # pylint: disable=unsubscriptable-object

    @classmethod
    def get_lock(cls, name: str) -> MongoLock:
        if cls.db_lock is None:
            cls.db_lock = MongoLock(collection=cls.get_collection("_lock"), name=name)
        return cls.db_lock
    

get_collection = LabgraphDefaultMongoDB.get_collection
get_lock = LabgraphDefaultMongoDB.get_lock

class LabgraphMongoDB:
    """
    A convenient wrapper for MongoClient. We can get a database object by calling ``get_collection`` function.
    """

    def __init__(self, host:str, port:int, db_name:str, username:Optional[str] = None, password:Optional[str] = None):
        self.client = pymongo.MongoClient(
            host=host,
            port=port,
            username=username or "",
            password=password or "",
        )
        self.db = self.client[db_name]

    def get_collection(self, name: str) -> collection.Collection:
        """
        Get collection by name
        """
        return self.db[name]

    def get_lock(self, name: str) -> MongoLock:
        return MongoLock(collection=self.get_collection("_lock"), name=name)
