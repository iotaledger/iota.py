Adapters and Wrappers
=====================

The ``Iota`` class defines the API methods that are available for
interacting with the node, but it delegates the actual interaction to
another set of classes: Adapters and Wrappers.

AdapterSpec
-----------

In a few places in the PyOTA codebase, you may see references to a
meta-type called ``AdapterSpec``.

``AdapterSpec`` is a placeholder that means "URI or adapter instance".

For example, the first argument of ``Iota.__init__`` is an
``AdapterSpec``. This means that you can initialize an ``Iota`` object
using either a node URI, or an adapter instance:

-  Node URI: ``Iota('http://localhost:14265')``
-  Adapter instance: ``Iota(HttpAdapter('http://localhost:14265'))``

Adapters
--------

Adapters are responsible for sending requests to the node and returning
the response.

PyOTA ships with a few adapters:

HttpAdapter
~~~~~~~~~~~

.. code:: python

    from iota import Iota
    from iota.adapter import HttpAdapter

    # Use HTTP:
    api = Iota('http://localhost:14265')
    api = Iota(HttpAdapter('http://localhost:14265'))

    # Use HTTPS:
    api = Iota('https://service.iotasupport.com:14265')
    api = Iota(HttpAdapter('https://service.iotasupport.com:14265'))

``HttpAdapter`` uses the HTTP protocol to send requests to the node.

To configure an ``Iota`` instance to use ``HttpAdapter``, specify an
``http://`` or ``https://`` URI, or provide an ``HttpAdapter`` instance.

The ``HttpAdapter`` raises a ``BadApiResponse`` exception if the server
sends back an error response (due to invalid request parameters, for
example).

Debugging HTTP Requests
^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from logging import getLogger

    from iota import Iota

    api = Iota('http://localhost:14265')
    api.adapter.set_logger(getLogger(__name__))

To see all HTTP requests and responses as they happen, attach a
``logging.Logger`` instance to the adapter via its ``set_logger``
method.

Any time the ``HttpAdapter`` sends a request or receives a response, it
will first generate a log message. Note: if the response is an error
response (e.g., due to invalid request parameters), the ``HttpAdapter``
will log the request before raising ``BadApiResponse``.

.. note::

    ``HttpAdapter`` generates log messages with ``DEBUG`` level, so make sure that your logger's ``level`` attribute is set low enough that it doesn't filter these messages!

SandboxAdapter
~~~~~~~~~~~~~~

.. code:: python

    from iota import Iota
    from iota.adapter.sandbox import SandboxAdapter

    api =\
      Iota(
        SandboxAdapter(
          uri = 'https://sandbox.iotatoken.com/api/v1/',
          auth_token = 'demo7982-be4a-4afa-830e-7859929d892c',
        ),
      )

The ``SandboxAdapter`` is a specialized ``HttpAdapter`` that sends
authenticated requests to sandbox nodes.

.. note::

    See `Sandbox <https://dev.iota.org/sandbox/>`_ Documentation for more information about sandbox nodes.

Sandbox nodes process certain commands asynchronously. When
``SandboxAdapter`` determines that a request is processed
asynchronously, it will block, then poll the node periodically until it
receives a response.

The result is that ``SandboxAdapter`` abstracts away the sandbox node's
asynchronous functionality so that your API client behaves exactly the
same as if it were connecting to a non-sandbox node.

To create a ``SandboxAdapter``, you must provide the URI of the sandbox
node and the auth token that you received from the node maintainer. Note
that ``SandboxAdapter`` only works with ``http://`` and ``https://``
URIs.

You may also specify the polling interval (defaults to 15 seconds) and
the number of polls before giving up on an asynchronous job (defaults to
8 times).

.. note::

    For parity with the other adapters, ``SandboxAdapter`` blocks until it receives a response from the node.

        If you do not want ``SandboxAdapter`` to block the main thread, it is recommended that you execute it in a separate thread or process.


MockAdapter
~~~~~~~~~~~

.. code:: python

    from iota import Iota
    from iota.adapter import MockAdapter

    # Inject a mock adapter.
    api = Iota('mock://')
    api = Iota(MockAdapter())

    # Seed responses from the node.
    api.adapter.seed_response('getNodeInfo', {'message': 'Hello, world!'})
    api.adapter.seed_response('getNodeInfo', {'message': 'Hello, IOTA!'})

    # Invoke API commands, using the adapter.
    print(api.get_node_info()) # {'message': 'Hello, world!'}
    print(api.get_node_info()) # {'message': 'Hello, IOTA!'}
    print(api.get_node_info()) # raises BadApiResponse exception

``MockAdapter`` is used to simulate the behavior of an adapter without
actually sending any requests to the node.

This is particularly useful in unit and functional tests where you want
to verify that your code works correctly in specific scenarios, without
having to engineer your own subtangle.

To configure an ``Iota`` instance to use ``MockAdapter``, specify
``mock://`` as the node URI, or provide a ``MockAdapter`` instance.

To use ``MockAdapter``, you must first seed the responses that you want
it to return by calling its ``seed_response`` method.

``seed_response`` takes two parameters:

-  ``command: Text``: The name of the command. Note that this is the
   camelCase version of the command name (e.g., ``getNodeInfo``, not
   ``get_node_info``).
-  ``response: dict``: The response that the adapter will return.

You can seed multiple responses for the same command; the
``MockAdapter`` maintains a queue for each command internally, and it
will pop a response off of the corresponding queue each time it
processes a request.

Note that you have to call ``seed_response`` once for each request you
expect it to process. If ``MockAdapter`` does not have a seeded response
for a particular command, it will raise a ``BadApiResponse`` exception
(simulates a 404 response).

Wrappers
--------

Wrappers act like decorators for adapters; they are used to enhance or
otherwise modify the behavior of adapters.

RoutingWrapper
~~~~~~~~~~~~~~

.. code:: python

    from iota import Iota
    from iota.adapter.wrappers import RoutingWrapper

    api =\
      Iota(
        # Send PoW requests to local node.
        # All other requests go to light wallet node.
        RoutingWrapper('https://service.iotasupport.com:14265')
          .add_route('attachToTangle', 'http://localhost:14265')
          .add_route('interruptAttachingToTangle', 'http://localhost:14265')
      )

``RoutingWrapper`` allows you to route API requests to different nodes
depending on the command name.

For example, you could use this wrapper to direct all PoW requests to a
local node, while sending the other requests to a light wallet node.

``RoutingWrapper`` must be initialized with a default URI/adapter. This
is the adapter that will be used for any command that doesn't have a
route associated with it.

Once you've initialized the ``RoutingWrapper``, invoke its ``add_route``
method to specify a different adapter to use for a particular command.

``add_route`` requires two arguments:

-  ``command: Text``: The name of the command. Note that this is the
   camelCase version of the command name (e.g., ``getNodeInfo``, not
   ``get_node_info``).
-  ``adapter: AdapterSpec``: The adapter or URI to send this request to.
