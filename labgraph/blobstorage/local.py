import os
from pathlib import Path
from typing import Any

from labgraph.utils import get_config
from uuid import uuid4
import pickle


class LocalBlob:
    def __init__(self, path: str = None):
        if path is None:
            config = get_config()
            blobstorage = config.get("blobstorage", {})
            local = blobstorage.get("local", {})
            localpath = local.get("path", None)
            if localpath is None:
                raise Exception(
                    "No local blobstorage path provided. Please provide a path in the config file."
                )
            path = config["blobstorage"]["local"]["path"]

        self.path = Path(path)

    def get(self, key: str):
        if not self.exists(key):
            raise Exception(f"Blob with ID {key} does not exist at path {self.path}.")
        path = self.path / key
        with open(path, "rb") as f:
            return pickle.load(f)

    def put(self, data: Any, key: str = None):
        if key is None:
            key = str(uuid4())

        path = self.path / key
        with open(path, "wb") as f:
            pickle.dump(data, f)

        return key

    def exists(self, key: str):
        return os.path.exists(self.path / key)


def get_local_blob(key: str) -> Any:
    local_blob = LocalBlob()
    return local_blob.get(key)


def put_local_blob(data: Any, key: str = None) -> str:
    local_blob = LocalBlob()
    return local_blob.put(data, key)
