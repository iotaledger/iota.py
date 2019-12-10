Installation
============
PyOTA is compatible with Python 3.7, 3.6, 3.5 and 2.7.

Install PyOTA using `pip`:

.. code-block:: bash

   pip install pyota[ccurl,pow]

.. note::

   The ``[ccurl]`` extra installs the optional `PyOTA-CCurl extension`_.

   This extension boosts the performance of certain crypto operations
   significantly (speedups of 60x are common).

.. py:currentmodule:: iota.Iota

.. _pow-label:

.. note::

   The ``[pow]`` extra installs the optional `PyOTA-PoW extension`_.

   This extension makes it possible to perform proof-of-work
   (api call ``attach_to_tangle``) locally, without relying on an iota node.
   Use the ``local_pow`` parameter at api instantiation:

   .. code::

      api = Iota('https://nodes.thetangle.org:443', local_pow=True)

   Or the :py:meth:`set_local_pow` method of the api class to dynamically
   enable/disable the local proof-of-work feature.

Getting Started
===============
In order to interact with the IOTA network, you will need access to a node.

You can:

- `Run your own node.`_
- `Use a light wallet node.`_

Note that light wallet nodes often disable certain features like PoW for
security reasons.

Once you've gotten access to an IOTA node, initialize an :py:class:`iota.Iota`
object with the URI of the node, and optional seed:

.. code-block:: python

   from iota import Iota

   # Generate a random seed.
   api = Iota('http://localhost:14265')

   # Specify seed.
   api = Iota('http://localhost:14265', 'SEED9GOES9HERE')

Test your connection to the server by sending a ``getNodeInfo`` command:

.. code-block:: python

   print(api.get_node_info())

You are now ready to send commands to your IOTA node!

.. _forum: https://forum.iota.org/
.. _official api: https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference
.. _pyota-ccurl extension: https://pypi.python.org/pypi/PyOTA-CCurl
.. _pyota-pow extension: https://pypi.org/project/PyOTA-PoW/
.. _run your own node.: http://iotasupport.com/headlessnode.shtml
.. _slack: http://slack.iota.org/
.. _use a light wallet node.: http://iotasupport.com/lightwallet.shtml
