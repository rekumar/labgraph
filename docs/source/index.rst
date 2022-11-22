.. ALab Data documentation master file, created by
   sphinx-quickstart on Tue Nov 22 09:49:05 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. note::

This project is under active development.


Welcome to ALab-Data's documentation!
=====================================
**ALab-Data** is a Python library for storing and retrieving materials science data stored in MongoDB. This library enforces a data model tailored for experimental materials data (computational or physical experiments). At a high-level, data is stored as a directed graph of four node types: Materials, Actions, Measurements, and Analyses. The content of these nodes is up to you -- we just make sure that any data you enter results in a valid graph. A more detailed description of the schema can be found in the :doc:`schema` section.

Node Types
''''''''''''
Here is a brief overview of the four node types and their roles in the data model.

- **Material** nodes are the fundamental building blocks of the data model. These represent a material in a given state. 

- **Action** nodes are operations that generate new Materials. Action nodes have incoming edges from any input Material(s) and outgoing edges to generated Material(s). An Action can generate Material(s) without consuming any input Material(s), as may be the case when procuring a Material from a vendor or receiving a Material from a collaborator. 

- **Measurement** nodes act upon a Material node to yield some form of raw data.

- **Analysis** nodes act upon a Measurement node to yield some form of processed data.


Samples = Graphs
'''''''''''''''''''
As materials scientists, we do controlled sets of Actions, Measurements, and Analyses to study a Material. In Alab-Data, one such set of nodes is referred to as a *Sample*. A Sample is simply a graph of nodes that captures the steps performed in an experiment. In typical usage, we will enter nodes into the database as part of a *Sample*. This achieves a few things:

- We can ensure that the graph we are entering is valid (i.e. it is a DAG with no isolated nodes).

- Given a node, we can easily retrieve the most related nodes that belong to the same Sample.

- We can record any Sample-level metadata (e.g. sample name, sample description, sample author, etc.) in a single place.


.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
