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
        n2 = View(labgraph_mongodb_instance=labgraph_mongo_obj).get_by_name(name)
        n3 = View(labgraph_mongodb_instance=default_labgraph_mongo_obj).get_by_name(name)
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
    View2 = views.MaterialView(labgraph_mongodb_instance=db2_instance)
    
    View1.add(m1)
    View2.add(m2)
    
    with pytest.raises(NotFoundInDatabaseError):
        View1.get(m2.id)
        
    with pytest.raises(NotFoundInDatabaseError):
        View2.get(m1.id)
        
    m2.save() #class methods go to the default database defined in Labgraph config
    View1.get(m2.id)
    
    drop_collections(labgraph_mongodb_instance=db2_instance)
        
        

        
        
        
        