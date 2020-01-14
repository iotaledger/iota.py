Tutorials
=========
Are you new to IOTA in Python? Don't worry, we got you covered! With the
walkthrough examples of this section, you will be a master of PyOTA.

In each section below, a code snippet will be shown and discussed in detail
to help you understand how to carry out specific tasks with PyOTA.

If you feel that something is missing or not clear, please post your questions
and suggestions in the `PyOTA Bug Tracker`_.

Let's get to it then!

.. py:currentmodule:: iota

Hello Node
----------
In this example, you will learn how to:

- **Import the** ``iota`` **package into your application.**
- **Instantiate an API object for communication with the IOTA network.**
- **Request information about the IOTA node you are connected to.**


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
.. code-block::
    :lineno-start: 1

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

.. code-block::
    :lineno-start: 5

    # Declare an API object
    api = Iota('https://nodes.devnet.iota.org:443')

Next, we declare an API object. Since this object handles the communication,
we need to specify an IOTA node to connect to in the form of an URI. Note, that
the library will parse this string and will throw an exception if it is not
a valid one.

.. code-block::
    :lineno-start: 8

    # Request information about the node
    response = api.get_node_info()

Then we can call the :py:meth:`Iota.get_node_info` method of the API
object to get some basic info about the node.

.. code-block::
    :lineno-start: 11

    # Using pprint instead of print for a nicer looking result in the console
    pprint(response)

Finally, we print out the response. It is important to note, that all API
methods return a python dictionary. Refer to the method's documentation to
determine what exactly is there in the response ``dict``. Here for example,
we could list the ``features`` of the node::

    pprint(response['features'])

Send Data
---------
In this example, you will learn how to:

- **Encode data to be stored on the Tangle.**
- **Generate a random IOTA address that doesn't belong to anyone.**
- **Create a zero-value transaction with custom payload.**
- **Send a transaction to the network.**

Code
~~~~
.. literalinclude:: ../examples/tutorials/02_send_data.py
   :linenos:

Discussion
~~~~~~~~~~
.. code-block::
    :lineno-start: 1

    from iota import Iota, TryteString, Address, Tag, ProposedTransaction
    from pprint import pprint

    # Declare an API object
    api = Iota('https://nodes.devnet.iota.org:443', testnet=True)

We have seen this part before. Note, that now we import more objects which we
will use to construct our transaction.

Notice ``testnet=True`` in the argument list of the API instantiation. We
tell the API directly that we will use the devnet/testnet. By default, the API
is configured for the mainnet.

.. code-block::
    :lineno-start: 7

    # Prepare custom data
    my_data = TryteString.from_unicode('Hello from the Tangle!')

If you read :ref:`Basic Concepts` and :ref:`PyOTA Types`, it shouldn't be a
surprise to you that most things in IOTA are represented as trytes, that are
:py:class:`TryteString` in PyOTA.

Here, we encode our message with :py:meth:`TryteString.from_unicode` into
trytes.

.. code-block::
    :lineno-start: 10

    # Generate a random address that doesn't have to belong to anyone
    my_address = Address.random()

To put anything (transactions) on the Tangle, it needs to be associated with
an address. **Since we will be posting a zero-value transaction, nobody has to
own this address**, therefore we can use the :py:meth:`TryteString.random` (an
:py:class:`Address` is just a :py:class:`TryteString` with some additional
attributes and fixed length) method to generate one.

.. code-block::
    :lineno-start: 13

    # Tag is optional here
    my_tag = Tag(b'MY9FIRST9TAG')

To tag our transaction, we might define a custom :py:class:`Tag` object. Notice,
that the ``b`` means we are creating a bytestring now. Each byte in it is
interpreted as a tryte, therefore we are restricted to the tryte aphabet.

.. code-block::
    :lineno-start: 16

    # Prepare a transaction object
    tx = ProposedTransaction(
        address=my_address,
        value=0,
        tag=my_tag,
        message=my_data
    )

It's time to construct the transaction. According to :ref:`Transaction Types`,
PyOTA uses :py:class:`ProposedTransaction` to build transactions that are not
yet broadcast to the network. Oberve, that the ``value=0`` means this is
a zero-value transaction.

.. code-block::
    :lineno-start: 24

    # Send the transaction to the network
    response = api.send_transfer([tx])

Next, we send the transfer to the node for tip selection,
proof-of-work calculation, broadcasting and storing. The API takes care of
all these tasks, and returns the resulting ``Bundle`` object.

.. note::

    :py:meth:`~Iota.send_transfer` takes a list of :py:class:`ProposedTransaction`
    objects as its ``transfers`` argument. An IOTA transfer (bundle) usually
    consists of multiple transactions linked together, however, in this simple
    example, there is only one transaction in the bundle. Regardless, you need
    to pass this sole transaction as a list of one transaction.

.. code-block::
    :lineno-start: 27

    pprint('Check your transaction on the Tangle!')
    pprint('https://utils.iota.org/transaction/%s/devnet' % response['bundle'][0].hash)

Finally, we print out the transaction's link on the Tangle Explorer.
Observe how we extract the transaction hash from the response ``dict``. We take
the first element of the bundle, as it is just a sequence of transactions, and
access its ``hash`` attribute.

.. _PyOTA Bug Tracker: https://github.com/iotaledger/iota.py/issues
.. _Tangle Explorer: https://utils.iota.org