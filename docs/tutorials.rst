Tutorials
=========
Are you new to IOTA in Python? Don't worry, we got you covered! With the
walkthrough examples of this section, you will be a master of PyOTA.

In each section below, a code snippet will be shown and discussed in detail
to help you understand how to carry out specific tasks with PyOTA.

If you feel that something is missing or not clear, please post your questions
and suggestions in the `PyOTA Bug Tracker`_.

Let's get to it then!

Hello World
-----------
In this example, you will learn how to:

- Import the ``iota`` package into your application.
- Instantiate an API object for communication with the IOTA network.
- Request information about the IOTA node you are connected to.

.. py:currentmodule:: iota

Code
~~~~
.. highlight:: python
   :linenothreshold: 5

.. code-block:: python

    # Import neccessary modules
    from iota import Iota
    from pprint import pprint

    # Declare an API object
    api = Iota('https://nodes.devnet.iota.org:443')

    # Request information about the node
    response = api.get_node_info()

    # Using pprint instead of print for a nicer looking result in the console
    pprint(response)

Discussion
~~~~~~~~~~
::

    # Import neccessary modules
    from iota import Iota
    from pprint import pprint

First things first, we need to import in our application the modules we intend
to use. PyOTA provide the ``iota`` package, therefore, whenever you need
something from the library, you need to import it from there.

Notice, how we import the :py:class:`Iota` object, that defines a
so-called extended API object. We will use this to send and receive data from
the network. Read more about API objects at :ref:`PyOTA API Classes`.

We also import the ``pprint`` method that prettifies the output before printing
it to the output.

::

    # Declare an API object
    api = Iota('https://nodes.devnet.iota.org:443')

Next, we declare an API object. Since this object handles the communication,
we need to specify an IOTA node to connect to in the form of an URI. Note, that
the library will parse this string and will throw an exception if it is not
a valid one.

::

    # Request information about the node
    response = api.get_node_info()

Then we can call the :py:meth:`Iota.get_node_info` method of the API
object to get some basic info about the node.

::

    # Using pprint instead of print for a nicer looking result in the console
    pprint(response)

Finally, we print out the response. It is important to note, that all API
methods return a python dictionary. Refer to the method's documentation to
determine what exactly is there in the response ``dict``. Here for example,
we could list the ``features`` of the node::

    pprint(response['features'])

.. _PyOTA Bug Tracker: https://github.com/iotaledger/iota.py/issues