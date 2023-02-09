from typing import List
import pytest
from labgraph import Actor, AnalysisMethod, views
from labgraph.utils.dev import drop_collections


@pytest.fixture
def add_actors_to_db():
    actorview = views.ActorView()
    labman = Actor(
        name="LabMan",
        tags=["SolidStateALab"],
        description="A robotic system that weighs and mixes powders in crucibles. Used to prepare samples for firing in furnaces. This is in building 30-105 at Lawrence Berkeley National Laboratory.",
    )

    tubefurnace1 = Actor(
        name="TubeFurnace1",
        tags=["SolidStateALab"],
        description="A tube furnace in building 30-105 at Lawrence Berkeley National Laboratory.",
    )

    aeris = Actor(
        name="Aeris",
        tags=["SolidStateALab"],
        description="An x-ray diffractometer. This is in building 30-105 at Lawrence Berkeley National Laboratory.",
    )

    operator = Actor(
        name="Operator",
        description="A generic actor for any operation performed by a human. No need to name names!",
    )

    actorview.add(labman)
    actorview.add(tubefurnace1)
    actorview.add(aeris)
    actorview.add(operator)

    yield

    drop_collections()


@pytest.fixture
def add_analysis_methods_to_db():
    analysismethodview = views.AnalysisMethodView()

    xrd = AnalysisMethod(
        name="Phase Identification",
        description="X-ray diffraction analysis",
        tags=["x-ray", "diffraction", "powder"],
    )

    density = AnalysisMethod(
        name="Density",
        description="Density measurement by Archimedes' principle",
        tags=["density", "mass", "volume", "powder"],
    )

    analysismethodview.add(xrd)
    analysismethodview.add(density)

    yield

    drop_collections()
