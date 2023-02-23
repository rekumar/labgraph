Setting up Labgraph
====================

Labgraph is a Python package that can be installed using pip. It is designed to work with MongoDB, a NoSQL database. When you interact with Labgraph, it is communicating with MongoDB to store and retrieve data. 

Installing Labgraph using pip
------------------------------

You can install Labgraph using pip:

.. code-block:: bash

    pip install labgraph

.. warning::

    Labgraph was written using Python 3.8, and is tested on Python 3.8, 3.9, 3.10. 


Installing MongoDB
-------------------
`MongoDB <http://mongodb.com>`_ is a `NoSQL <https://en.wikipedia.org/wiki/NoSQL>`_ database that is used to store and retrieve data. Labgraph uses MongoDB to store and retrieve data. MongoDB can be `installed on your local machine <https://www.mongodb.com/docs/manual/installation/>`_, or you can use a cloud service such as `MongoDB Atlas <https://www.mongodb.com/cloud/atlas>`_. 

Wherever you run MongoDB, you will need to know the host and port number. If you are running MongoDB locally, by default the host will be ``localhost`` and the port will be ``27017``. If you are using MongoDB Atlas, you will need to know the host and port number provided by MongoDB Atlas. These values are used to connect to MongoDB.

.. note:: 

    **A Quick MongoDB primer**

    Your MongoDB instance can hold multiple `databases`. Each `database` can hold multiple `collections`, and each `collection` can hold multiple `documents`. A `document` is a single data entry, which is basically a JSON object. Labgraph will create its own `database` (by default named "Labgraph") in your MongoDB instance, in which it will create `collections` for each type of Labgraph data (nodes, actors, samples, etc). Each node will be a `document` in its respective `collection`.  


The Labgraph Config File
-------------------------
Labgraph needs to know how to find your MongoDB instance. This is done using a config file. You will only need to set this up once unless your MongoDB information changes. 

The config file is a TOML file that contains the information needed to connect to MongoDB. An example is shown below. The "username" and "password" fields are optional, depending on whether your MongoDB instance requires authentication. 

.. code:: toml

    [mongodb]
    host = "localhost"
    port = 27017
    db_name = "Labgraph"
    username = "my_username"
    password = "my_password"

Labgraph provides a helper function `labgraph.utils.make_config` to make this file. Running this will walk you through the process of creating the config file. This function provides default values which are set for a local MongoDB instance. 


.. code-block:: python

    from labgraph.utils import make_config
    make_config()

By default this config file will be created inside the Labgraph package directory. You can put this config file wherever you want -- if it is not in the default location, however, you need to set an environment variable `LABGRAPH_CONFIG` to point to the location of the config file.

