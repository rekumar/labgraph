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
from bson import ObjectId
import random
from labgraph.data.groups import action_sequence_distance
import datetime


def test_NodeUpdates(add_single_sample):
    materialview = views.MaterialView()
    m = materialview.get_by_name("Titanium Dioxide")[0]
    m.parameters["formula"] = "TiO2"
    materialview.update(m)

    m_ = materialview.get(m.id)
    assert m_.parameters["formula"] == "TiO2"

    actionview = views.ActionView()
    p = actionview.get_by_name("grind")[0]
    p.parameters["final_step"] = True
    actionview.update(p)

    p_ = actionview.get(p.id)
    assert p_.parameters["final_step"] == True

    measurementview = views.MeasurementView()
    me = measurementview.get_by_name("XRD")[0]
    me.parameters["metadata"] = {"temperature": 300}
    measurementview.update(me)

    me_ = measurementview.get(me.id)
    assert me_.parameters["metadata"] == {"temperature": 300}

    analysisview = views.AnalysisView()
    a = analysisview.get_by_name("Phase Identification")[0]
    a.parameters["metadata"] = {"temperature": 300}
    analysisview.update(a)

    a_ = analysisview.get(a.id)
    assert a_.parameters["metadata"] == {"temperature": 300}


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

