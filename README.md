# ALab Data

> **Warning**
> This project is still under development!

This library defines a graph-based schema for storing materials science data. 

You can read the (evolving) documentation [here](https://alab-data.readthedocs.io/en/latest/index.html).




## Additional Dependencies

- A `Sample` graph can be plotted within Python using `Sample.plot()`. The default `networkx` plotting layouts can be pretty confusing to interpret. If you install [graphviz](https://www.graphviz.org), `alab_data` will instead use graphviz to design the graph layout in a hierarchical fashion. This only affects plotting, but if you are relying on this functionality it can make a big difference!
