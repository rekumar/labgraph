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
from labgraph.utils.data_objects import LabgraphMongoDB, LabgraphDefaultMongoDB
from labgraph.utils.dev import drop_collections


def test_NodeViews(add_single_sample):
    test_guide = {
        Material: "Titanium Dioxide",
        Action: "grind",
        Measurement: "XRD",
        Analysis: "Phase Identification",
    }
    
    view_guide = {
        Material: views.MaterialView,
        Action: views.ActionView,
        Measurement: views.MeasurementView,
        Analysis: views.AnalysisView,
    }

    db_info = {
        "host": "localhost",
        "port": 27017,
        "db_name": "xxxxxxxxLabgraph_Test",
    }
    
    labgraph_mongo_obj = LabgraphMongoDB(**db_info)
    default_labgraph_mongo_obj = LabgraphDefaultMongoDB()
    
    for node_class, name in test_guide.items():
        View = view_guide[node_class]
        n1 = View().get_by_name(name)
        n2 = View(conn=labgraph_mongo_obj).get_by_name(name)
        n3 = View(conn=default_labgraph_mongo_obj).get_by_name(name)
        n4 = node_class.get_by_name(name)
        assert n1 == n2 == n3 == n4
        
        
def test_NodeView_AcrossDBs():
    m1 = Material("This is a node to copy across both the default and second database")
    m2 = Material("This is a node to only put in the second database")
    
    second_db_info = {
        "host": "localhost",
        "port": 27017,
        "db_name": "xxxxxxxLabgraph_Test_2",
    }
    View1 = views.MaterialView()
    db2_instance = LabgraphMongoDB(**second_db_info)
    View2 = views.MaterialView(conn=db2_instance)
    
    View1.add(m1)
    View2.add(m2)
    
    with pytest.raises(NotFoundInDatabaseError):
        View1.get_by_id(m2.id)
        
    with pytest.raises(NotFoundInDatabaseError):
        View2.get_by_id(m1.id)
        
    m2.save() #class methods go to the default database defined in Labgraph config
    View1.get_by_id(m2.id)
    
    drop_collections(conn=db2_instance)
        
        
def test_FullSampleAcrossDBs():
    
    second_db_info = {
        "host": "localhost",
        "port": 27017,
        "db_name": "xxxxxxxLabgraph_Test_2",
    }
    db_instance = LabgraphMongoDB(**second_db_info)
    av = views.ActorView(conn=db_instance)
    
    operator = Actor(name="Operatorr", description="The person who did the work")
    aeris = Actor(name="Aeris", description="The XRD instrument")
    tubefurnace1 = Actor(name="TubeFurnace1", description="The tube furnace")
    xrd = Actor(name="Phase Identification", description="The XRD analysis")
    
    av.add(operator)
    av.add(aeris)
    av.add(tubefurnace1)
    av.add(xrd)
    
    operator = av.get_by_name(name="Operatorr")[0]
    aeris = av.get_by_name(name="Aeris")[0]
    tubefurnace1 = av.get_by_name(name="TubeFurnace1")[0]
    xrd = av.get_by_name(name="Phase Identification")[0]


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

    a0 = Analysis(name="Phase Identification", measurements=[me0], actor=xrd)

    # make a sample
    alab_sample = Sample(
        name="first sample", nodes=[m0, p0, p1, p2, p3, m3, m1, m2, me0, a0]
    )

    with pytest.raises(NotFoundInDatabaseError):
        views.SampleView().add(alab_sample)
    
    sample_view = views.SampleView(conn=db_instance)
    sample_view.add(alab_sample)

    alab_sample_ = sample_view.get_by_id(alab_sample.id)
    assert alab_sample_.name == "first sample"

    # make sure all individual nodes were added successfully
    view_dict = {
        Measurement: views.MeasurementView(conn=db_instance),
        Analysis: views.AnalysisView(conn=db_instance),
        Action: views.ActionView(conn=db_instance),
        Material: views.MaterialView(conn=db_instance),
    }
    for node in alab_sample._nodes:
        view = view_dict[type(node)]
        assert view.get_by_id(node.id) == node

    with pytest.raises(AlreadyInDatabaseError):
        sample_view.add(alab_sample)
        
        
    sample_view.remove(id=alab_sample.id, remove_nodes=False)
    sample_view.add(alab_sample)
    with pytest.raises(NotImplementedError):
        sample_view.remove(id=alab_sample.id, remove_nodes=True)

        
        
        
        