.. _node-types:

Node Types
===========

Material
""""""""

- :py:class:`Material <labgraph.Material>` nodes are the fundamental building blocks of the data model. These represent a material in a given state. 


.. autoclass:: labgraph.data.nodes.Material

    .. automethod:: __init__




Action
""""""""

- :py:class:`Action <labgraph.Action>` nodes are operations that generate new :py:class:`Material <labgraph.Material>`s. :py:class:`Action <labgraph.Action>` nodes have incoming edges from any input :py:class:`Material <labgraph.Material>`(s) and outgoing edges to generated :py:class:`Material <labgraph.Material>`(s). An :py:class:`Action <labgraph.Action>` can generate :py:class:`Material <labgraph.Material>`(s) without consuming any input :py:class:`Material <labgraph.Material>`(s), as may be the case when procuring a :py:class:`Material <labgraph.Material>` from a vendor or receiving a :py:class:`Material <labgraph.Material>` from a collaborator. 

Measurement
""""""""""""
- :py:class:`Measurement <labgraph.Measurement>` nodes act upon a :py:class:`Material <labgraph.Material>` node to yield some form of raw data.


Analysis
""""""""""
- :py:class:`Analysis <labgraph.Analysis>` nodes act upon a :py:class:`Measurement <labgraph.Measurement>` node to yield some form of processed data.
