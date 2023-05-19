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
from labgraph.views import get_view, get_view_by_type
from bson import ObjectId
import random
from labgraph.data.sample import action_sequence_distance

### helper


def build_a_sample(name: str) -> ObjectId:
    """Assumes that "add_single_sample" fixture has been run

    Args:
        name (str): sample name

    Returns:
        ObjectId: id for newly created sample
    """

    av = views.ActorView()
    labman: Actor = av.get_by_name(name="LabMan")[0]
    tubefurnace1: Actor = av.get_by_name(name="TubeFurnace1")[0]
    aeris: Actor = av.get_by_name(name="Aeris")[0]
    operator = av.get_by_name(name="Operator")[0]

    amv = views.AnalysisMethodView()
    xrd: AnalysisMethod = amv.get_by_name(name="Phase Identification")[0]

    # procure material
    m0 = views.MaterialView().get_by_name("Titanium Dioxide")[0]

    p1 = Action(
        "grind",
        ingredients=[
            Ingredient(
                material=m0,
                amount=random.choice([1, 1.5, 2]),
                unit="g",
            )
        ],
        actor=operator,
    )

    p2 = Action(
        "sinter",
        temperature=random.choice([800, 900, 1000]),
        time=random.choice([1, 2, 3]),
        actor=tubefurnace1,
    )

    p3 = Action("grind", actor=operator, final_step=True)

    # make a sample
    alab_sample = Sample(name=name)
    alab_sample.add_linear_process([p1, p2, p3])
    m_final = alab_sample.nodes[-1]

    me0 = Measurement(
        name="XRD",
        material=m_final,
        actor=aeris,
    )

    a0 = Analysis(name="Phase Identification", measurements=[me0], analysis_method=xrd)

    alab_sample.add_node(me0)
    alab_sample.add_node(a0)

    return views.SampleView().add(alab_sample)


### tests


def test_AddSample(add_actors_to_db, add_analysis_methods_to_db):
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

    # make sure all individual nodes were added successfully
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


def test_AddLinearSample(add_actors_to_db, add_analysis_methods_to_db):
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

    p2 = Action("sinter", actor=tubefurnace1)

    p3 = Action("grind", actor=operator, final_step=True)

    # make a sample
    alab_sample = Sample(name="first sample")
    alab_sample.add_linear_process([p0, p1, p2, p3])
    m_final = alab_sample.nodes[-1]

    me0 = Measurement(
        name="XRD",
        material=m_final,
        actor=aeris,
    )

    a0 = Analysis(name="Phase Identification", measurements=[me0], analysis_method=xrd)

    alab_sample.add_node(me0)
    alab_sample.add_node(a0)

    assert alab_sample.has_valid_graph == True

    assert views.SampleView().add(alab_sample) == alab_sample.id


def test_ActionGraph(add_single_sample):
    sample_id1 = build_a_sample("sample1")
    sample_id2 = build_a_sample("sample2")

    sv = views.SampleView()
    sample1 = sv.get(sample_id1)
    sample2 = sv.get(sample_id2)

    assert action_sequence_distance(sample1, sample2) == 0


def test_PlotSample(add_single_sample):
    sv = views.SampleView()
    sample = sv.get_by_name("first sample")[0]
    sample.plot()


def test_SampleEquality(add_single_sample):
    sv = views.SampleView()
    sample1 = sv.get_by_name("first sample")[0]
    sample1_ = sv.get_by_name("first sample")[0]

    assert sample1 == sample1_

    sampleid_2 = build_a_sample("sample2")
    sample2 = sv.get(sampleid_2)
    assert sample1 != sample2


def test_QueryByNode(add_single_sample):
    mv = views.MaterialView()
    m = mv.get_by_name("Titanium Dioxide")[0]

    sv = views.SampleView()
    samples = sv.get_by_node(m)
    assert len(samples) == 1


def test_SampleUpdate(add_single_sample):
    sv = views.SampleView()
    sample = sv.get_by_name("first sample")[0]

    # simple change
    sample.name = "updated sample name"
    sv.update(sample)
    sample_ = sv.get_by_name("updated sample name")[0]

    assert sample == sample_

    # graph change
    final_material = sample.nodes[-3]

    operator = views.ActorView().get_by_name("Operator")[0]
    p4 = Action("grind", ingredients=[WholeIngredient(final_material)], actor=operator)
    new_final_material = p4.make_generic_generated_material()
    sample.add_node(p4)
    sample.add_node(new_final_material)

    sv.update(sample)
    sample_ = sv.get_by_name("updated sample name")[0]

    assert sample == sample_


def test_SampleDeletionKeepNodes(add_single_sample):
    sv = views.SampleView()
    sample = sv.get_by_name("first sample")[0]

    sv.remove(sample.id, remove_nodes=False, _force_dangerous=True)

    with pytest.raises(NotFoundInDatabaseError):
        sv.get_by_name("first sample")

    # make sure nodes are still in the database
    for node in sample.nodes:
        assert views.get_view(node).get(node.id) == node


def test_SampleDeletionDeleteNodes(add_single_sample):
    sv = views.SampleView()
    sample = sv.get_by_name("first sample")[0]

    sv.remove(sample.id, remove_nodes=True, _force_dangerous=True)

    with pytest.raises(NotFoundInDatabaseError):
        sv.get_by_name("first sample")

    # make sure nodes are still in the database
    for node in sample.nodes:
        view = get_view(node)
        assert view._exists(node.id) == False


def test_SampleDeletionMultipleSamplesAffected(add_single_sample):
    sample_id1 = build_a_sample("sample1")
    sample_id2 = build_a_sample("sample2")

    sv = views.SampleView()
    sample1 = sv.get(sample_id1)
    sample2 = sv.get(sample_id2)

    # delete sample1
    sv.remove(sample1.id, remove_nodes=True, _force_dangerous=True)

    # make sure sample2 is still in the database
    with pytest.raises(NotFoundInDatabaseError):
        sv.get(sample1.id)

    with pytest.raises(NotFoundInDatabaseError):
        sv.get(sample2.id)


def test_NodeDeletionMultipleSamplesAffected(add_single_sample):
    sample_id1 = build_a_sample("sample1")
    sample_id2 = build_a_sample("sample2")

    sv = views.SampleView()
    sample1 = sv.get(sample_id1)
    sample2 = sv.get(sample_id2)

    node_to_delete = sample1.nodes[0]  # this material is shared across all samples

    # delete sample1
    views.get_view(node_to_delete).remove(node_to_delete.id, _force_dangerous=True)

    # make sure sample2 is still in the database
    with pytest.raises(NotFoundInDatabaseError):
        sv.get(sample1.id)

    with pytest.raises(NotFoundInDatabaseError):
        sv.get(sample2.id)


def test_Sample_classmethods(add_single_sample):
    cls = Sample
    name = "first sample"

    node = cls.get_by_name(name)[0]
    assert node.name == name

    node["new_field"] = "new_value"
    node.tags.append("new_tag")
    node.save()

    node_ = cls.get_by_name(name)[0]
    assert node == node_
    assert "new_field" in node_.keys()
    assert node["new_field"] == "new_value"

    node_ = cls.get(node.id)
    assert node == node_

    nodes_ = cls.get_by_tags(["new_tag"])
    assert node in nodes_

    nodes_ = cls.filter({"new_field": "new_value"})
    assert node in nodes_

    node_ = cls.filter_one({"new_field": "new_value"})
    assert node == node_
