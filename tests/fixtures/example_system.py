from typing import List
import pytest
from labgraph import Actor, views
from labgraph.utils.dev import drop_collections


@pytest.fixture
def add_actors_to_db():
    actorview = views.ActorView()
    labman = Actor(
        name="LabMan",
        tags=["SolidStateALab", "hardware"],
        description="A robotic system that weighs and mixes powders in crucibles. Used to prepare samples for firing in furnaces. This is in building 30-105 at Lawrence Berkeley National Laboratory.",
    )

    tubefurnace1 = Actor(
        name="TubeFurnace1",
        tags=["SolidStateALab", "hardware"],
        description="A tube furnace in building 30-105 at Lawrence Berkeley National Laboratory.",
    )

    aeris = Actor(
        name="Aeris",
        tags=["SolidStateALab", "hardware"],
        description="An x-ray diffractometer. This is in building 30-105 at Lawrence Berkeley National Laboratory.",
    )

    operator = Actor(
        name="Operator",
        description="A generic actor for any operation performed by a human. No need to name names!",
    )

    xrd = Actor(
        name="Phase Identification",
        description="X-ray diffraction analysis",
        tags=["x-ray", "diffraction", "powder", "analysis_script"],
    )

    density = Actor(
        name="Density",
        description="Density measurement by Archimedes' principle",
        tags=["density", "mass", "volume", "powder", "analysis_script"],
    )

    actorview.add(labman)
    actorview.add(tubefurnace1)
    actorview.add(aeris)
    actorview.add(operator)
    actorview.add(xrd)
    actorview.add(density)

    yield

    drop_collections()
