[![Documentation Status](https://readthedocs.org/projects/labgraph/badge/?version=latest)](https://labgraph.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/rekumar/labgraph/branch/master/graph/badge.svg?token=TUCYBZI2P4)](https://codecov.io/gh/rekumar/labgraph)

`pip install labgraph-db`

<picture>
 <source media="(prefers-color-scheme: dark)" srcset="./docs/source/img/logo/labgraph_dark mode.png">
 <source media="(prefers-color-scheme: light)" srcset="./docs/source/img/logo/labgraph_light mode.png">
 <img alt="LabGraph: a graph-based schema for storing experimental data for chemistry and materials science." src="./docs/source/img/logo/labgraph_light mode.png">
</picture>

> **Warning**
> This project is still under development!



This library defines a graph-based schema for storing materials science data. 

You can read the (evolving) documentation [here](https://labgraph.readthedocs.io/en/latest/).

I gave a talk on Labgraph at the 2023 Spring meeting for the Materials Research Society. You can view the slides [here](https://www.slideshare.net/secret/pevc4VHK5ThSr6), though the animations don't work. They key point is that we use labgraph as a central database to coordinate our automated lab like so:

<p style="text-align:center;">
<img src="./docs/figures/closedloop_example.gif"  style="width:100%; max-width: 600px;" loop=infinite>
</p>



## Additional Dependencies

- A `Sample` graph can be plotted within Python using `Sample.plot()`. The default `networkx` plotting layouts can be pretty confusing to interpret. If you install [graphviz](https://www.graphviz.org), `labgraph` will instead use graphviz to design the graph layout in a hierarchical fashion. This only affects plotting, but if you are relying on this functionality it can make a big difference!
