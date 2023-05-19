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
from labgraph.data.sample import action_sequence_distance
import datetime


def test_NodeUpdates(add_single_sample):
    materialview = views.MaterialView()
    m = materialview.get_by_name("Titanium Dioxide")[0]
    m._user_fields["formula"] = "TiO2"
    materialview.update(m)

    m_ = materialview.get(m.id)
    assert m_._user_fields["formula"] == "TiO2"

    m._user_fields["upstream"] = "this shouldnt be allowed"
    with pytest.raises(ValueError):
        materialview.update(
            m
        )  # we cant put user fields that collide with labgraph default keys.

    actionview = views.ActionView()
    p = actionview.get_by_name("grind")[0]
    p._user_fields["final_step"] = True
    actionview.update(p)

    p_ = actionview.get(p.id)
    assert p_._user_fields["final_step"] == True

    measurementview = views.MeasurementView()
    me = measurementview.get_by_name("XRD")[0]
    me._user_fields["metadata"] = {"temperature": 300}
    measurementview.update(me)

    me_ = measurementview.get(me.id)
    assert me_._user_fields["metadata"] == {"temperature": 300}

    analysisview = views.AnalysisView()
    a = analysisview.get_by_name("Phase Identification")[0]
    a._user_fields["metadata"] = {"temperature": 300}
    analysisview.update(a)

    a_ = analysisview.get(a.id)
    assert a_._user_fields["metadata"] == {"temperature": 300}


def test_NodeAddition(add_actors_to_db, add_analysis_methods_to_db):
    # material
    m = Material(
        name="Yttrium Oxide",
        formula="Y2O3",
        tags=["oxide", "Y"],
    )
    materialview = views.MaterialView()
    materialview.add(m)

    m_ = materialview.get_by_name("Yttrium Oxide")[0]
    assert m == m_

    # action
    operator = views.ActorView().get_by_name(name="Operator")[0]

    p = Action(
        name="procurement",
        generated_materials=[m],
        actor=operator,
    )
    actionview = views.ActionView()
    actionview.add(p)

    p_ = actionview.get_by_name("procurement")[0]
    assert p == p_

    # measurement
    aeris = views.ActorView().get_by_name(name="Aeris")[0]

    me = Measurement(
        name="XRD",
        scan_rate=1,
        scan_range=(0, 10),
        counts=[1, 2, 3, 1, 5, 1],
        material=m,
        actor=aeris,
    )
    measurementview = views.MeasurementView()
    measurementview.add(me)

    me_ = measurementview.get_by_name("XRD")[0]
    assert me == me_

    ##analysis
    # one measurement upstream
    phase_id = views.AnalysisMethodView().get_by_name(name="Phase Identification")[0]

    a = Analysis(
        name="Phase Identification",
        measurements=[me],
        analysis_method=phase_id,
    )
    analysisview = views.AnalysisView()
    analysisview.add(a)

    a_ = analysisview.get_by_name("Phase Identification")[0]
    assert a == a_

    # one analysis upstream
    a2 = Analysis(
        name="Figure of Merit",
        upstream_analyses=[a],
        analysis_method=phase_id,
    )
    analysisview.add(a2)

    a2_ = analysisview.get_by_name("Figure of Merit")[0]
    assert a2 == a2_

    # two analyses upstream
    a3 = Analysis(
        name="Figure of Merit2",
        upstream_analyses=[a, a2],
        analysis_method=phase_id,
    )
    analysisview.add(a3)

    a3_ = analysisview.get_by_name("Figure of Merit2")[0]
    assert a3 == a3_

    # two measurements upstream
    me2 = Measurement(
        name="XRD",
        scan_rate=1,
        scan_range=(0, 10),
        counts=[1, 2, 3, 1, 10, 1],
        material=m,
        actor=aeris,
    )
    measurementview.add(me2)

    a4 = Analysis(
        name="Figure of Merit3",
        extra_field="extra",
        measurements=[me, me2],
        analysis_method=phase_id,
    )
    analysisview.add(a4)

    a4_ = analysisview.get_by_name("Figure of Merit3")[0]
    assert a4 == a4_

    # two measurements and two analyses upstream
    a5 = Analysis(
        name="Figure of Merit4",
        measurements=[me, me2],
        upstream_analyses=[a, a2],
        analysis_method=phase_id,
    )
    analysisview.add(a5)

    a5_ = analysisview.get_by_name("Figure of Merit4")[0]
    assert a5 == a5_


def test_NodeFilterByTime():
    m = Material(
        name="Yttrium Oxide",
    )
    m2 = Material(
        name="Barium Oxide",
    )
    materialview = views.MaterialView()
    _id = materialview.add(m)
    _id2 = materialview.add(m2)

    now = datetime.datetime.now()
    older = now - datetime.timedelta(days=1)

    materialview._collection.update_one(
        {"_id": _id},
        {"$set": {"created_at": older}},
    )

    assert (
        len(materialview.filter({}, datetime_min=older - datetime.timedelta(minutes=1)))
        == 2
    )
    assert (
        len(materialview.filter({}, datetime_min=older + datetime.timedelta(minutes=1)))
        == 1
    )

    assert (
        len(materialview.filter({}, datetime_max=older + datetime.timedelta(minutes=1)))
        == 1
    )


def test_NodeDeletion(add_single_sample):
    # deleting a node without any downstream nodes
    s = views.SampleView().get_by_name("first sample")[0]
    original_node_length = len(s.nodes)
    node_to_delete = s.nodes[-1]
    get_view(node_to_delete).remove(node_to_delete.id, _force_dangerous=True)

    s = views.SampleView().get_by_name("first sample")[0]
    assert len(s.nodes) == original_node_length - 1

    # deleting a node with upstream and downstream nodes
    s = views.SampleView().get_by_name("first sample")[0]
    node_to_delete = s.nodes[-3]
    original_node_length = len(s.nodes)
    get_view(node_to_delete).remove(node_to_delete.id, _force_dangerous=True)

    s = views.SampleView().get_by_name("first sample")[0]
    assert len(s.nodes) == original_node_length - 3

    # deleting a node with only downstream nodes
    s = views.SampleView().get_by_name("first sample")[0]
    node_to_delete = s.nodes[0]
    get_view(node_to_delete).remove(node_to_delete.id, _force_dangerous=True)

    with pytest.raises(NotFoundInDatabaseError):
        # the sample should be deleted since all its nodes are also deleted
        views.SampleView().get_by_name("first sample")


def test_Node_classmethods(add_single_sample):
    test_guide = {
        Material: "Titanium Dioxide",
        Action: "grind",
        Measurement: "XRD",
        Analysis: "Phase Identification",
    }

    for cls, name in test_guide.items():
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
