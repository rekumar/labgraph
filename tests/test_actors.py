import pytest
from labgraph import Actor, AnalysisMethod
from labgraph.views import ActorView, AnalysisMethodView
from labgraph.views.base import AlreadyInDatabaseError, NotFoundInDatabaseError


def test_ActorView(clean_db):
    ## adding an actor
    a = Actor(
        name="test_actor", description="test actor", tags=["test_tag1", "test_tag2"]
    )
    av = ActorView()
    av.add(a)

    a_ = av.get_by_name(name="test_actor")[0]
    assert a.to_dict() == a_.to_dict()

    ## adding an actor that already exists
    with pytest.raises(AlreadyInDatabaseError):
        av.add(a)

    assert av.add(a, if_already_in_db="skip") == a.id

    assert av.add(a, if_already_in_db="update") == a.id


def test_AnalysisMethodView(clean_db):
    ## adding an AnalysisMethod
    am = AnalysisMethod(
        name="test_analysis_method",
        description="test analysis method",
        tags=["test_tag1", "test_tag2"],
    )
    amv = AnalysisMethodView()
    amv.add(am)

    am_ = amv.get_by_name(name="test_analysis_method")[0]
    assert am.to_dict() == am_.to_dict()

    ## adding an AnalysisMethod that already exists
    assert amv.add(am, if_already_in_db="skip") == am.id

    assert amv.add(am, if_already_in_db="update") == am.id


def test_ActorVersioning(add_actors_to_db):
    av = ActorView()
    labman: Actor = av.get_by_name(name="LabMan")[0]
    labman.tags.append("new_tag")
    av.update(labman)
    labman_ = av.get_by_name(name="LabMan")[0]
    assert labman_.tags == ["SolidStateALab", "new_tag"]

    labman = av.get_by_name(name="LabMan")[0]
    labman.new_version(description="This is what changed when upgrading this Actor")
    av.update(labman)

    labman_ = av.get_by_name(name="LabMan")[0]
    assert labman_.version == 2


def test_AnalysisMethodVersioning(add_analysis_methods_to_db):

    amv = AnalysisMethodView()
    xrd: AnalysisMethod = amv.get_by_name(name="Phase Identification")[0]
    xrd.tags.append("new_tag")
    amv.update(xrd)
    xrd_ = amv.get_by_name(name="Phase Identification")[0]
    assert xrd_.tags == ["x-ray", "diffraction", "powder", "new_tag"]

    xrd.new_version(
        description="This is what changed when upgrading this AnalysisMethod"
    )
    assert xrd.version == 2
    amv.update(xrd)
    xrd_ = amv.get_by_name(name="Phase Identification")[0]
    assert xrd_.version == 2


def test_Actor_retrieval(add_actors_to_db):
    av = ActorView()

    labman = av.get_by_name(name="LabMan")[0]
    tubefurnace = av.get_by_name(name="TubeFurnace1")[0]
    aeris = av.get_by_name(name="Aeris")[0]

    results = av.get_by_tags(["SolidStateALab"])
    for r in results:
        assert r in [labman, tubefurnace, aeris]

    assert av.filter_one({"name": "LabMan"}) == labman

    assert av.filter({"name": "LabMan"})[0] == labman

    with pytest.raises(NotFoundInDatabaseError):
        av.get_by_name("Random name that doesnt exist")


def test_AnalysisMethod_retrieval(add_analysis_methods_to_db):
    av = AnalysisMethodView()

    xrd = av.get_by_name(name="Phase Identification")[0]
    density = av.get_by_name(name="Density")[0]

    results = av.get_by_tags(["powder"])
    for r in results:
        assert r in [xrd, density]

    assert av.filter_one({"name": "Phase Identification"}) == xrd

    assert av.filter({"name": "Density"})[0] == density

    with pytest.raises(NotFoundInDatabaseError):
        av.get_by_name("Random name that doesnt exist")
