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

To use the API in your Python application or script, declare an
API instance of any of the two above.
**Since the Extended API incorporates the Core API, usually you end up only
using the Extended API,** but if for some reason you need only the core
functionality, the library is there to help you.

.. code-block::
   :linenos:
   :emphasize-lines: 3,4

   from iota import Iota, StrictIota

   # This is how you declare an Extended API, use the methods of this object.
   api = Iota('adapter-specification')

   # This is how you declare a Core API, use the methods of this object.
   api = StrictIota('adapter-specification')

.. py:module:: iota

The PyOTA speific :py:class:`StrictIota` class implements the Core API,
while :py:class:`Iota` implements the Extended API. From a Python
implementation point of view, :py:class:`Iota` is a subclass of
:py:class:`StrictIota`, therefore it inherits every method and attribute
the latter has.

Take a look on the class definitions and notice that :py:class:`Iota`
has a :py:class:`Seed` attribute. This is becasue the Extended API is able
to generate private keys, addresses and signatures from your seed.
**Your seed never leaves the library and your machine!**

Core API Class
--------------

.. autoclass:: StrictIota
    :members: set_local_pow

Extended API Class
------------------

.. autoclass:: Iota
    :members: set_local_pow
