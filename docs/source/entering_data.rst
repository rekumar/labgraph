.. warning::
    This page is a work in progress that is mostly incomplete!

Entering Data
==============

First, we create the nodes themselves. Second, we create a Sample and attribute the nodes to it. Finally, we add the Sample to our database using the SampleView.

###############
Creating Nodes
###############

The construction of each node type follows mostly the same process. There are a few required properties for each node.

==================
Common Properties
==================
The properties common to all nodes are:

- name (string, required): the name of the node. This does not need to be unique. In some cases it may even be desirable to have multiple nodes with the same name (ie all Action nodes that describe procurement of reagents could be named "Procurement")
- tags (list[string], optional): strings by which to tag the node. This could be useful for searching for nodes with a particular tag. For example, all nodes that describe procurement of reagents could be tagged "procurement".

=========================
Node-Specific Properties
=========================

Material Nodes

.. code-block:: python
    :linenos:

    from alab_data import Material

    material_node = Material(
        name="Titanium Dioxide" #required argument
        tags=["reagent"], #optional argument
    )

Action Nodes

.. code-block:: python
    :linenos:

    from alab_data import Action, Ingredient, Actor
    from alab_data.views import ActorView

    actor_view = ActorView()
    mortar_and_pestle = Actor(
        name="Mortar and Pestle" #required argument
        description="A mortar and pestle is a device used since ancient times to prepare ingredients or substances by crushing and grinding them into a fine paste or powder." #optional argument
        tags = ["hand tools", "morphology"]
    )
    actor_view.add(mortar_and_pestle)

    action_node = Action(
        name="Grinding" #required argument
        ingredients = [
            Ingredient(
                material = material_node, #required argument
                quantity = 1, #required argument
                unit = "g" #required argument
            )
        ],
        actor = mortar_and_pestle
    )

Measurement Nodes

.. code-block:: python
    :linenos:

    from alab_data import Measurement, Actor
    from alab_data.views import ActorView

    actor_view = ActorView()
    xrd_instrument = Actor(
        name="Bruker D8 Advance" #required argument
        description="The Bruker D8 Advance is a high-resolution X-ray diffractometer that can be used to determine the crystal structure of a material." #optional argument
        tags = ["XRD", "crystal structure"]
    )
    actor_view.add(xrd_instrument)

    measurement_node = Measurement(
        name="XRD" #required argument
        material=material_node, #required argument
        actor=xrd_instrument #required argument
    )

Analysis Nodes

.. code-block:: python
    :linenos:

    from alab_data import Analysis, Actor
    from alab_data.views import AnalysisMethodView

    analysismethod_view = AnalysisMethodView()
    phase_identification_method = AnalysisMethod(
        name="Phase Identification", #required argument
        description="Phase identification is the process of determining the phases present in a material.", #optional argument
        tags = ["XRD", "crystal structure"],
        version = "1.0.0",
        github_link = "https://github.com/myrepo/phase_identification"
    )
    analysismethod_view.add(phase_identification_method)

    phase_identification_method = analysismethod_view.get("Phase Identification") #in case method was already in your database

    analysis_node = Analysis(
        name="XRD" #required argument
        material=material_node, #required argument
        analysis_method=phase_identification_method #required argument
    )


==========================
Adding your data to nodes
==========================
All the examples above show the minimum information required to create a node. However, you probably want to add your own metadata to these nodes too! This is really easy -- just pass them as keyword arguments to the node constructor. For example, if you wanted to add a description to your material node, you could do:

.. code-block:: python
    :linenos:

    material_node = Material(
        name="Titanium Dioxide" #required argument
        tags=["reagent"], #optional argument
        description="Titanium dioxide is a white solid that is insoluble in water. It is commonly used as a pigment in paints, inks, plastics, paper, sunscreen, food coloring, and cosmetics." #your own extra field!
    )

Other common examples include adding process parameters to an Action node:

.. code-block:: python
    :linenos:

    action_node = Action(
        name="Annealing" #required argument
        ingredients = [
            Ingredient(
                material = material_node, #required argument
                quantity = 1, #required argument
                unit = "g" #required argument
            )
        ],
        actor = furnace,
        temperature_celsius = 1500, #your own extra field!
        duration_minutes = 240 #your own extra field!
    )

and, of course, adding raw data to a Measurement node:

.. code-block:: python
    :linenos:

    measurement_node = Measurement(
        name="XRD" #required argument
        material=material_node, #required argument
        actor=xrd_instrument #required argument
        data = {
            "2theta": [10, 20, 30, 40, 50],
            "intensity": [0, 17.5, 12.1, 1.3, 0]
        } #your own extra field!
    )

.. note::
    Whatever data you put in your nodes will eventually be encoded as BSON to be stored in MongoDB. This means that you can't use any data types that `BSON doesn't support <https://pymongo.readthedocs.io/en/stable/api/bson/index.html>`_. For example, you can't use a numpy array as a value in your data dictionary. You can, however, use a list. If you want to use a numpy array, you should convert it to a list first.