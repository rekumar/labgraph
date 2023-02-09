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
from labgraph.views.base import AlreadyInDatabaseError, NotFoundInDatabaseError


@pytest.mark.usefixtures("add_actors_to_db", "add_analysis_methods_to_db")
def test_Sample():
    ## get actors and analysis methods
    av = views.ActorView()
    operator = av.get_by_name(name="Operator")[0]
    aeris = av.get_by_name(name="Aeris")[0]
    tubefurnace1 = av.get_by_name(name="TubeFurnace1")[0]

    amv = views.AnalysisMethodView()
    xrd: AnalysisMethod = amv.get_by_name(name="Phase Identification")[0]

    # define sample nodes
    m0 = Material(
        name="Titanium Dioxide",
        formula="TiO2",
    )

    p0 = Action(
        name="procurement",
        generated_materials=[m0],
        actor=operator,
    )

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

    # make a sample
    alab_sample = Sample(
        name="first sample", nodes=[m0, p0, p1, p2, p3, m3, m1, m2, me0, a0]
    )

    assert alab_sample.has_valid_graph == True

    assert views.SampleView().add(alab_sample) == alab_sample.id

    alab_sample_ = views.SampleView().get(alab_sample.id)
    assert alab_sample_.name == "first sample"

    #make sure all individual nodes were added successfully
    view_dict = {
        Measurement: views.MeasurementView(),
        Analysis: views.AnalysisView(),
        Action: views.ActionView(),
        Material: views.MaterialView(),
    }
    for node in alab_sample.nodes:
        view = view_dict[type(node)]
        assert view.get(node.id) == node
    
    
    with pytest.raises(AlreadyInDatabaseError):
        views.SampleView().add(alab_sample)

    