Adapters and Wrappers
=====================
.. py:currentmodule:: iota

The :py:class:`Iota` class defines the API methods that are available for
interacting with the node, but it delegates the actual interaction to
another set of classes: `Adapters <#adapters>`__ and `Wrappers <#wrappers>`__.

The API instance's methods contain the logic and handle PyOTA-specific types,
construct and translate objects, while the API instance's adapter deals with
the networking, communicating with a node.

You can choose and configure the available adapters to be used with the API:

 - HttpAdapter,
 - SandboxAdapter,
 - MockAdapter.

AdapterSpec
-----------


In a few places in the PyOTA codebase, you may see references to a
meta-type called ``AdapterSpec``.

.. automodule:: iota.adapter
    :special-members: AdapterSpec

.. py:currentmodule:: iota

For example, when creating an :py:class:`Iota` object, the first argument
of :py:meth:`Iota.__init__` is an ``AdapterSpec``. This means that you can
initialize an :py:class:`Iota` object using either a node URI, or an adapter
instance:

-  Node URI::

     api = Iota('http://localhost:14265')

-  Adapter instance::

     api = Iota(HttpAdapter('http://localhost:14265'))

Adapters
--------

Adapters are responsible for sending requests to the node and returning
the response.

PyOTA ships with a few adapters:

HttpAdapter
~~~~~~~~~~~

.. code:: python

    from iota import Iota, HttpAdapter

    # Use HTTP:
    api = Iota('http://localhost:14265')
    api = Iota(HttpAdapter('http://localhost:14265'))

    # Use HTTPS:
    api = Iota('https://nodes.thetangle.org:443')
    api = Iota(HttpAdapter('https://nodes.thetangle.org:443'))

    # Use HTTPS with basic authentication and 60 seconds timeout:
    api = Iota(
        HttpAdapter(
            'https://nodes.thetangle.org:443',
            authentication=('myusername', 'mypassword'),
            timeout=60))

.. autoclass:: HttpAdapter

To configure an :py:class:`Iota` instance to use :py:class:`HttpAdapter`,
specify an ``http://`` or ``https://`` URI, or provide an
:py:class:`HttpAdapter` instance.

The :py:class:`HttpAdapter` raises a ``BadApiResponse`` exception if the server
sends back an error response (due to invalid request parameters, for
example).

Debugging HTTP Requests
^^^^^^^^^^^^^^^^^^^^^^^
To see all HTTP requests and responses as they happen, attach a
``logging.Logger`` instance to the adapter via its ``set_logger``
method.

Any time the :py:class:`HttpAdapter` sends a request or receives a response, it
will first generate a log message. Note: if the response is an error
response (e.g., due to invalid request parameters), the :py:class:`HttpAdapter`
will log the request before raising ``BadApiResponse``.

.. note::

    :py:class:`HttpAdapter` generates log messages with ``DEBUG`` level, so make
    sure that your logger's ``level`` attribute is set low enough that it
    doesn't filter these messages!

**Logging to console with default format**

.. code:: python

    from logging import getLogger, basicConfig, DEBUG
    from iota import Iota

    api = Iota("https://nodes.thetangle.org:443")

    # Sets the logging level for the root logger (and for its handlers)
    basicConfig(level=DEBUG)

    # Get a new logger derived from the root logger
    logger = getLogger(__name__)

    # Attach the logger to the adapter
    api.adapter.set_logger(logger)

    # Execute a command that sends request to the node
    api.get_node_info()

    # Log messages should be printed to console

**Logging to a file with custom format**

.. code:: python

    from logging import getLogger, DEBUG, FileHandler, Formatter
    from iota import Iota

    # Create a custom logger
    logger = getLogger(__name__)

    # Set logging level to DEBUG
    logger.setLevel(DEBUG)

    # Create handler to write to a log file
    f_handler = FileHandler(filename='pyota.log',mode='a')
    f_handler.setLevel(DEBUG)

    # Create formatter and add it to handler
    f_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    # Add handler to the logger
    logger.addHandler(f_handler)

    # Create API instance
    api = Iota("https://nodes.thetangle.org:443")

    # Add logger to the adapter of the API instance
    api.adapter.set_logger(logger)

    # Sends a request to the node
    api.get_node_info()

    # Open 'pyota.log' file and observe the logs

**Logging to console with custom format**

.. code:: python

    from logging import getLogger, DEBUG, StreamHandler, Formatter
    from iota import Iota

    # Create a custom logger
    logger = getLogger(__name__)

    # Set logging level to DEBUG
    logger.setLevel(DEBUG)

    # Create handler to write to sys.stderr
    s_handler = StreamHandler()
    s_handler.setLevel(DEBUG)

    # Create formatter and add it to handler
    s_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s_handler.setFormatter(s_format)

    # Add handler to the logger
    logger.addHandler(s_handler)

    # Create API instance
    api = Iota("https://nodes.thetangle.org:443")

    # Add logger to the adapter of the API instance
    api.adapter.set_logger(logger)

    # Sends a request to the node
    api.get_node_info()

    # Observe log messages in console

MockAdapter
~~~~~~~~~~~

.. code:: python

    from iota import Iota, MockAdapter

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

.. autoclass:: MockAdapter

To use :py:class:`MockAdapter`, you must first seed the responses that you want
it to return by calling its :py:meth:`MockAdapter.seed_response` method.

**seed_response**
^^^^^^^^^^^^^^^^^
.. automethod:: MockAdapter.seed_response

Wrappers
--------

Wrappers act like decorators for adapters; they are used to enhance or
otherwise modify the behavior of adapters.

RoutingWrapper
~~~~~~~~~~~~~~
.. autoclass:: iota.adapter.wrappers.RoutingWrapper

**add_route**
^^^^^^^^^^^^^
.. automethod:: iota.adapter.wrappers.RoutingWrapper.add_route