import time
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
    m._contents["formula"] = "TiO2"
    materialview.update(m)

    m_ = materialview.get_by_id(m.id)
    assert m_._contents["formula"] == "TiO2"
    assert m_.get("formula") == "TiO2"
    assert m_.get("nonexistent_key", "default_value") == "default_value"
    with pytest.raises(KeyError):
        m_["nonexistent_key"]
    with pytest.raises(KeyError):
        m_.get("nonexistent_key")

    m._contents["upstream"] = "this shouldnt be allowed"
    with pytest.raises(ValueError):
        materialview.update(
            m
        )  # we cant put user fields that collide with labgraph default keys.

    actionview = views.ActionView()
    p = actionview.get_by_name("grind")[0]
    p._contents["final_step"] = True
    actionview.update(p)

    p_ = actionview.get_by_id(p.id)
    assert p_._contents["final_step"] == True

    current_actors = p_.actor
    new_actor = Actor.get_by_name("LabMan")
    p_.add_actor(Actor.get_by_name("LabMan"))
    p_.save()
    p__ = actionview.get_by_id(p.id)
    assert all(a in p__.actor for a in current_actors + [new_actor])

    p_.remove_actor(new_actor)
    p_.save()
    p__ = actionview.get_by_id(p.id)
    assert new_actor not in p__.actor

    with pytest.raises(ValueError):
        p_.remove_actor(new_actor)  # cant remove an actor that isnt in the node already
    

    measurementview = views.MeasurementView()
    me = measurementview.get_by_name("XRD")[0]
    me._contents["metadata"] = {"temperature": 300}
    measurementview.update(me)

    me_ = measurementview.get_by_id(me.id)
    assert me_._contents["metadata"] == {"temperature": 300}

    analysisview = views.AnalysisView()
    a = analysisview.get_by_name("Phase Identification")[0]
    a._contents["metadata"] = {"temperature": 300}
    last_updated_at = a.updated_at
    time.sleep(1)
    analysisview.update(a)
    new_updated_at = a.updated_at
    assert new_updated_at > last_updated_at

    a_ = analysisview.get_by_id(a.id)
    assert a_._contents["metadata"] == {"temperature": 300}
    assert a_.updated_at == new_updated_at
    


def test_NodeAddition(add_actors_to_db):
    # material
    m = Material(
        name="Yttrium Oxide",
        formula="Y2O3",
        tags=["oxide", "Y"],
    )
    materialview = views.MaterialView()
    assert m._created_at is None  # not yet added to the db
    assert m._updated_at is None
    assert isinstance(m.created_at, str)  # gives a message explaining not yet added
    assert isinstance(m.updated_at, str)  # gives a message explaining not yet added

    materialview.add(m)
    assert isinstance(m._created_at, datetime.datetime)  # now added to the db
    assert isinstance(m._updated_at, datetime.datetime)

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
    phase_id = views.ActorView().get_by_name(name="Phase Identification")[0]

    a = Analysis(
        name="Phase Identification",
        measurements=[me],
        actor=phase_id,
    )
    analysisview = views.AnalysisView()
    analysisview.add(a)

    a_ = analysisview.get_by_name("Phase Identification")[0]
    assert a == a_

    # one analysis upstream
    a2 = Analysis(
        name="Figure of Merit",
        upstream_analyses=[a],
        actor=phase_id,
    )
    analysisview.add(a2)

    a2_ = analysisview.get_by_name("Figure of Merit")[0]
    assert a2 == a2_

    # two analyses upstream
    a3 = Analysis(
        name="Figure of Merit2",
        upstream_analyses=[a, a2],
        actor=phase_id,
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
        actor=phase_id,
    )
    analysisview.add(a4)

    a4_ = analysisview.get_by_name("Figure of Merit3")[0]
    assert a4 == a4_

    # two measurements and two analyses upstream
    a5 = Analysis(
        name="Figure of Merit4",
        measurements=[me, me2],
        upstream_analyses=[a, a2],
        actor=phase_id,
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
        len(materialview.find({}, datetime_min=older - datetime.timedelta(minutes=1)))
        == 2
    )
    assert (
        len(materialview.find({}, datetime_min=older + datetime.timedelta(minutes=1)))
        == 1
    )

    assert (
        len(materialview.find({}, datetime_max=older + datetime.timedelta(minutes=1)))
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

        node_ = cls.get_by_id(node.id)
        assert node == node_

        nodes_ = cls.get_by_tags(["new_tag"])
        assert node in nodes_

        nodes_ = cls.filter({"contents.new_field": "new_value"})
        assert node in nodes_

        node_ = cls.filter_one({"contents.new_field": "new_value"})
        assert node == node_


def test_Node_laziness(add_single_sample):
    test_guide = {
        Material: "Titanium Dioxide",
        Action: "grind",
        Measurement: "XRD",
        Analysis: "Phase Identification",
    }

    # Material
    node = Material.get_by_name("Titanium Dioxide")[0]
    node1 = Material.from_dict(node.to_dict())
    assert node == node1

    # Action
    node = Action.get_by_name("grind")[0]
    assert node.generated_materials[0].name == "Titanium Dioxide - grind"
    node1 = Action.from_dict(node.to_dict())
    assert node == node1
    assert node1.generated_materials[0].name == "Titanium Dioxide - grind"

    newmaterial = Material(name="new material")
    newaction = Action(
        name="new action",
        actor=Actor.get_by_name("LabMan"),
        generated_materials=[newmaterial],
    )
    assert newaction.generated_materials[0].name == "new material"
    newaction1 = Action.from_dict(newaction.to_dict())
    with pytest.raises(NotFoundInDatabaseError):
        # the generated material wasnt added to the database, so we cant pull the material nodes from the db
        newaction1.generated_materials

    # Measurement
    node = Measurement.get_by_name("XRD")[0]
    assert node.material.name == "Titanium Dioxide - grind - sinter - grind"
    node1 = Measurement.from_dict(node.to_dict())
    assert node == node1
    assert node1.material.name == "Titanium Dioxide - grind - sinter - grind"

    newmeasurement = Measurement(
        name="new measurement",
        actor=Actor.get_by_name("Aeris"),
        material=newmaterial,
    )
    assert newmeasurement.material.name == "new material"
    newmeasurement1 = Measurement.from_dict(newmeasurement.to_dict())
    with pytest.raises(NotFoundInDatabaseError):
        # the material wasnt added to the database, so we cant pull the material nodes from the db
        newmeasurement1.material

    # Analysis
    node = Analysis.get_by_name("Phase Identification")[0]
    assert node.measurements[0].name == "XRD"
    node1 = Analysis.from_dict(node.to_dict())
    assert node == node1

    newanalysis = Analysis(
        name="new analysis",
        actor=Actor.get_by_name("Phase Identification"),
        measurements=[newmeasurement],
        upstream_analyses=[node],
    )
    assert newanalysis.measurements[0].name == "new measurement"
    assert newanalysis.upstream_analyses[0].name == "Phase Identification"
    newanalysis1 = Analysis.from_dict(newanalysis.to_dict())
    with pytest.raises(NotFoundInDatabaseError):
        # the measurement wasnt added to the database, so we cant pull the measurement nodes from the db
        newanalysis1.measurements
    assert newanalysis1.upstream_analyses[0].name == "Phase Identification"

    newanalysis2 = Analysis(
        name="new analysis2",
        actor=Actor.get_by_name("Phase Identification"),
        measurements=[newmeasurement],
        upstream_analyses=[newanalysis],
    )
    assert newanalysis2.measurements[0].name == "new measurement"
    assert newanalysis2.upstream_analyses[0].name == "new analysis"
    newanalysis2_ = Analysis.from_dict(newanalysis2.to_dict())
    with pytest.raises(NotFoundInDatabaseError):
        # the measurement wasnt added to the database, so we cant pull the measurement nodes from the db
        newanalysis2_.measurements
    with pytest.raises(NotFoundInDatabaseError):
        # the upstream analysis wasnt added to the database, so we cant pull the upstream analysis nodes from the db
        newanalysis2_.upstream_analyses
