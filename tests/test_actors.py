import pytest
from labgraph import Actor
from labgraph.views import ActorView
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


def test_ActorVersioning(add_actors_to_db):
    av = ActorView()
    labman: Actor = av.get_by_name(name="LabMan")[0]
    labman.tags.append("new_tag")
    av.update(labman)
    labman_ = av.get_by_name(name="LabMan")[0]
    assert "new_tag" in labman_.tags

    labman = av.get_by_name(name="LabMan")[0]
    labman.new_version(description="This is what changed when upgrading this Actor")
    av.update(labman)

    labman_ = av.get_by_name(name="LabMan")[0]
    assert labman_.version == 2


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


def test_Actor_invalid_fields(add_actors_to_db):
    view = ActorView()
    test_actor = Actor(
        name="test_actor_with_invalid_fields",
        description="test actor",
        version="test_version",
    )
    with pytest.raises(ValueError):
        view.add(
            test_actor
        )  # the "version" field would collide with a LabGraph default field, and shouldn't be allowed!


def test_Actor_classmethods(clean_db):
    a = Actor(
        name="test_actor", description="test actor", tags=["test_tag1", "test_tag2"]
    )
    a.save()

    a_ = Actor.get_by_name(name="test_actor")
    assert a == a_

    a__ = Actor.filter_one({"name": "test_actor"})
    assert a == a__

    a___ = Actor.filter({"name": "test_actor"})[0]

    assert a == a___

    a_ = Actor.get_by_tags(["test_tag1", "test_tag2"])[0]
    assert a == a_

    a_ = Actor.get_by_tags(["test_tag1"])[0]
    assert a == a_

    a["new_user_field"] = "new_user_field_value"
    a.save()

    a_ = Actor.get_by_name(name="test_actor")

    assert a_["new_user_field"] == "new_user_field_value"
    assert a_.keys() == ["new_user_field"]
    assert a == a_
