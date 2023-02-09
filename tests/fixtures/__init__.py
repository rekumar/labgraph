import pytest

from .example_system import *
from .example_data import *


@pytest.fixture
def clean_db():
    drop_collections()
    yield
    drop_collections()
