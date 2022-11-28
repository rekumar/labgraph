.. _node-types:

Node Types
===========

Material
""""""""

- :py:class:`Material <alab_data.Material>` nodes represent a material in a given state/at a certain point within an experiment. "Material" here is used loosely -- in essence, a :py:class:`Material <alab_data.Material>` node is what an experimentalist might consider their "sample". For example, a :py:class:`Material <alab_data.Material>` could describe a chemical, a solution, a powder, or a thin film. 


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
