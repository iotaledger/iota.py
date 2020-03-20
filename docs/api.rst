PyOTA API Classes
=================

**PyOTA offers you the Python API to interact with the IOTA network.
The available methods can be grouped into two categories:**

+------------------------------------+------------------------------------+
|              Core API              |            Extended API            |
+====================================+====================================+
|                                    |                                    |
|                                    | | Builds on top of the Core API to |
| |  API commands for direct         | | perform more complex operations, |
| |  interaction with a node.        | | and abstract away low-level IOTA |
|                                    | | specific procedures.             |
|                                    |                                    |
+------------------------------------+------------------------------------+

**PyOTA supports both synchronous and asynchronous communication with the network,
therefore the Core and Extended API classes are available in synchronous and
asynchronous versions.**

To use the API in your Python application or script, declare an
API instance of any of the API classes.
**Since the Extended API incorporates the Core API, usually you end up only
using the Extended API,** but if for some reason you need only the core
functionality, the library is there to help you.

.. code-block::
   :linenos:
   :emphasize-lines: 3,4

   # Synchronous API classes
   from iota import Iota, StrictIota

   # This is how you declare a sync Extended API, use the methods of this object.
   api = Iota('adapter-specification')

   # This is how you declare a sync Core API, use the methods of this object.
   api = StrictIota('adapter-specification')

.. py:module:: iota

The PyOTA speific :py:class:`StrictIota` class implements the Core API,
while :py:class:`Iota` implements the Extended API. From a Python
implementation point of view, :py:class:`Iota` is a subclass of
:py:class:`StrictIota`, therefore it inherits every method and attribute
the latter has.

To use the functionally same, but asynchronous API classes, you can do the
following:

.. code-block::
   :linenos:
   :emphasize-lines: 3,4

   # Asynchronous API classes
   from iota import AsyncIota, AsyncStrictIota

   # This is how you declare an async Extended API, use the methods of this object.
   api = AsyncIota('adapter-specification')

   # This is how you declare an async  Core API, use the methods of this object.
   api = AsyncStrictIota('adapter-specification')


Take a look on the class definitions and notice that :py:class:`Iota` and
:py:class:`AsyncIota` have a :py:class:`Seed` attribute. This is because the
Extended API is able to generate private keys, addresses and signatures from
your seed. **Your seed never leaves the library and your machine!**

Core API Classes
----------------
Synchronous
^^^^^^^^^^^
.. autoclass:: StrictIota
    :members: set_local_pow

Asynchronous
^^^^^^^^^^^^
.. autoclass:: AsyncStrictIota
    :members: set_local_pow

Extended API Classes
--------------------
Synchronous
^^^^^^^^^^^
.. autoclass:: Iota
    :members: set_local_pow

Asynchronous
^^^^^^^^^^^^
.. autoclass:: AsyncIota
    :members: set_local_pow
