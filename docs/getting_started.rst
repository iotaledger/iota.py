Installation
============
PyOTA is compatible with Python 3.7, 3.6, 3.5 and 2.7.

Install PyOTA using `pip`:

.. code-block:: bash

   pip install pyota[ccurl]

.. note::

   The ``[ccurl]`` extra installs the optional `PyOTA-CCurl extension`_.

   This extension boosts the performance of certain crypto operations
   significantly (speedups of 60x are common).

Getting Started
===============
In order to interact with the IOTA network, you will need access to a node.

You can:

- `Run your own node.`_
- `Use a light wallet node.`_
- `Use the sandbox node.`_

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

Using the Sandbox Node
----------------------
To connect to the sandbox node, you will need to inject a
:py:class:`SandboxAdapter` into your :py:class:`Iota` object.  This will modify
your API requests so that they contain the necessary authentication metadata.

.. code-block:: python

   from iota.adapter.sandbox import SandboxAdapter

   api = Iota(
     # To use sandbox mode, inject a ``SandboxAdapter``.
     adapter = SandboxAdapter(
       # URI of the sandbox node.
       uri = 'https://sandbox.iotatoken.com/api/v1/',

       # Access token used to authenticate requests.
       # Contact the node maintainer to get an access token.
       auth_token = 'auth token goes here',
     ),

     # Seed used for cryptographic functions.
     # If null, a random seed will be generated.
     seed = b'SEED9GOES9HERE',
   )

.. _forum: https://forum.iota.org/
.. _official api: https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference
.. _pyota-ccurl extension: https://pypi.python.org/pypi/PyOTA-CCurl
.. _run your own node.: http://iotasupport.com/headlessnode.shtml
.. _slack: http://slack.iota.org/
.. _use a light wallet node.: http://iotasupport.com/lightwallet.shtml
.. _use the sandbox node.: http://dev.iota.org/sandbox
