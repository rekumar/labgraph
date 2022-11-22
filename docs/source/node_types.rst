.. _node-types:

Node Types
===========

Material
""""""""

- :py:class:`Material <alab_data.Material>` nodes are the fundamental building blocks of the data model. These represent a material in a given state. 


.. autoclass:: alab_data.data.nodes.Material

    .. automethod:: __init__




Action
""""""""

- :py:class:`Action <alab_data.Action>` nodes are operations that generate new :py:class:`Material <alab_data.Material>`s. :py:class:`Action <alab_data.Action>` nodes have incoming edges from any input :py:class:`Material <alab_data.Material>`(s) and outgoing edges to generated :py:class:`Material <alab_data.Material>`(s). An :py:class:`Action <alab_data.Action>` can generate :py:class:`Material <alab_data.Material>`(s) without consuming any input :py:class:`Material <alab_data.Material>`(s), as may be the case when procuring a :py:class:`Material <alab_data.Material>` from a vendor or receiving a :py:class:`Material <alab_data.Material>` from a collaborator. 

Measurement
""""""""""""
- :py:class:`Measurement <alab_data.Measurement>` nodes act upon a :py:class:`Material <alab_data.Material>` node to yield some form of raw data.


Analysis
""""""""""
- :py:class:`Analysis <alab_data.Analysis>` nodes act upon a :py:class:`Measurement <alab_data.Measurement>` node to yield some form of processed data.
