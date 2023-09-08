from typing import Optional
from labgraph.utils.data_objects import LabgraphMongoDB
from labgraph import Actor, Action, Material, Measurement, Analysis, Sample, Ingredient, WholeIngredient, views
from labgraph.utils.dev import drop_collections
import numpy as np

def _make_example_actors(conn: Optional[LabgraphMongoDB] = None):
    actorview = views.ActorView(conn=conn)
    labman = Actor(
        name="LabMan",
        tags=["SolidStateALab", "hardware"],
        description="A robotic system that weighs and mixes powders in crucibles. Used to prepare samples for firing in furnaces. This is in building 30-105 at Lawrence Berkeley National Laboratory.",
    )

    tubefurnace1 = Actor(
        name="TubeFurnace1",
        tags=["SolidStateALab", "hardware"],
        description="A tube furnace in building 30-105 at Lawrence Berkeley National Laboratory.",
    )

    aeris = Actor(
        name="Aeris",
        tags=["SolidStateALab", "hardware"],
        description="An x-ray diffractometer. This is in building 30-105 at Lawrence Berkeley National Laboratory.",
    )

    operator = Actor(
        name="Operator",
        description="A generic actor for any operation performed by a human. No need to name names!",
    )

    xrd = Actor(
        name="Phase Identification",
        description="X-ray diffraction analysis",
        tags=["x-ray", "diffraction", "powder", "analysis_script"],
    )

    density = Actor(
        name="Density",
        description="Density measurement by Archimedes' principle",
        tags=["density", "mass", "volume", "powder", "analysis_script"],
    )

    actorview.add(labman)
    actorview.add(tubefurnace1)
    actorview.add(aeris)
    actorview.add(operator)
    actorview.add(xrd)
    actorview.add(density)
    
    
__example_materials = [
    ("Titanium Dioxide", "TiO2"),
    ("Lithium Cobalt Oxide", "LiCoO2"),
    ("Aluminum Oxide", "Al2O3"),
]

def _make_example_procurement(conn: Optional[LabgraphMongoDB] = None):
    operator = views.ActorView(conn=conn).get_by_name(name="Operator")[0]
    for (name, formula) in __example_materials:
        m0 = Material(
            name=name,
            formula=formula,
        )

        p0 = Action(
            name="procurement",
            generated_materials=[m0],
            actor=operator,
        )

        procurement_sample = Sample(name="procurement", nodes=[p0, m0])
        views.SampleView(conn=conn).add(procurement_sample)
         
def _make_example_sample(name: str, description:str = "an example sample", conn: Optional[LabgraphMongoDB] = None, **contents):
    av = views.ActorView(conn=conn)
    labman: Actor = av.get_by_name(name="LabMan")[0]
    tubefurnace1: Actor = av.get_by_name(name="TubeFurnace1")[0]
    aeris: Actor = av.get_by_name(name="Aeris")[0]
    operator = av.get_by_name(name="Operator")[0]
    xrd: Actor = av.get_by_name(name="Phase Identification")[0]
    
    mv = views.MaterialView(conn=conn)
    
    m0 = mv.get_by_name(name=np.random.choice([m[0] for m in __example_materials]))[0]

    # make a sample
    p1 = Action(
        "grind",
        ingredients=[
            Ingredient(
                material=m0,
                amount=np.random.uniform(0.1, 0.5),
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
        result={
            "twotheta": [10,20,30,40,50],
            "intensity": [1,2,5,2,1],
        }
    )

    a0 = Analysis(name="Phase Identification", measurements=[me0], actor=xrd, result={"phase": np.random.choice(["anatase TiO2", "LiCoO3"])})
    alab_sample = Sample(name=name, description=description, nodes=[p1, p2, p3, m3, m1, m2, me0, a0], **contents)
    views.SampleView(conn).add(alab_sample)
    
def make_example_database(conn: Optional[LabgraphMongoDB] = None):
    drop_collections(conn=conn)
    _make_example_actors(conn=conn)
    _make_example_procurement(conn=conn)
    for i in range(20):
        _make_example_sample(name=f"sample{i}", conn=conn)
    