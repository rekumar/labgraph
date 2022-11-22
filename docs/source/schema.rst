Data Schema
============

All data is stored as a `directed acyclic graph (DAG) <https://en.wikipedia.org/wiki/Directed_acyclic_graph>`_. The "direction" of edges encodes the order that nodes (ie experimental steps) were performed in. The "acyclic" constraint ensures that nodes cannot connect upstream to older nodes, which would be travelling back in time!

The four :ref:`node types <node-types>` are designed to cover capture the generation of materials, the measurement of these materials, and analysis of these measurements. 