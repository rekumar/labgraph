from typing import List
import pytest
from labgraph import (
    Action,
    Material,
    Measurement,
    Analysis,
    Ingredient,
    WholeIngredient,
    Sample,
    Actor,
    AnalysisMethod,
    views,
)
from labgraph.utils.dev import drop_collections
from .example_system import add_actors_to_db, add_analysis_methods_to_db


@pytest.fixture
def add_single_sample(add_actors_to_db, add_analysis_methods_to_db):
    # get your actors and analysis methods
    av = views.ActorView()
    labman: Actor = av.get_by_name(name="LabMan")[0]
    tubefurnace1: Actor = av.get_by_name(name="TubeFurnace1")[0]
    aeris: Actor = av.get_by_name(name="Aeris")[0]
    operator = av.get_by_name(name="Operator")[0]

    amv = views.AnalysisMethodView()
    xrd: AnalysisMethod = amv.get_by_name(name="Phase Identification")[0]

    # procure material
    m0 = Material(
        name="Titanium Dioxide",
        formula="TiO2",
    )

    p0 = Action(
        name="procurement",
        generated_materials=[m0],
        actor=operator,
    )

    procurement_sample = Sample(name="procurement", nodes=[p0, m0])
    views.SampleView().add(procurement_sample)

    # make a sample
    p1 = Action(
        "grind",
        ingredients=[
            Ingredient(
                material=m0,
                amount=1,
                unit="g",
            )
        ],
        actor=operator,
    )
    m1 = p1.make_generic_generated_material()

    p2 = Action("sinter", ingredients=[WholeIngredient(m1)], actor=tubefurnace1)
    m2 = p2.make_generic_generated_material()

    p3 = Action(
        "grind", ingredients=[WholeIngredient(m2)], actor=operator, final_step=True
    )
    m3 = p3.make_generic_generated_material()

    me0 = Measurement(
        name="XRD",
        material=m3,
        actor=aeris,
    )

    a0 = Analysis(name="Phase Identification", measurements=[me0], analysis_method=xrd)
    alab_sample = Sample(name="first sample", nodes=[p1, p2, p3, m3, m1, m2, me0, a0])
    views.SampleView().add(alab_sample)
