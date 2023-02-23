import pytest

from .example_system import *
from .example_data import *
import os
import toml
import pymongo


@pytest.fixture(autouse=True)
def make_config_file():
    config_path = os.path.abspath(os.path.join(os.curdir, "labgraph_test_config.toml"))

    config = {
        "mongodb": {
            "host": "localhost",
            "port": 27017,
            "db_name": "Labgraph_Test",
        }
    }
    with open(config_path, "w") as f:
        toml.dump(config, f)
    os.environ["LABGRAPH_CONFIG"] = config_path

    yield

    os.remove(config_path)
    del os.environ["LABGRAPH_CONFIG"]
    pymongo.MongoClient(
        host=config["mongodb"]["host"],
        port=config["mongodb"]["port"],
    ).drop_database(config["mongodb"]["db_name"])


@pytest.fixture
def clean_db():
    drop_collections()
    yield
    drop_collections()
