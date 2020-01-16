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

1. Hello Node
-------------
In this example, you will learn how to:

- **Import the** ``iota`` **package into your application.**
- **Instantiate an API object for communication with the IOTA network.**
- **Request information about the IOTA node you are connected to.**


Code
~~~~
.. literalinclude:: ../examples/tutorials/01_hello_node.py
   :linenos:

Discussion
~~~~~~~~~~
.. literalinclude:: ../examples/tutorials/01_hello_node.py
   :lines: 1-3
   :lineno-start: 1

First things first, we need to import in our application the modules we intend
to use. PyOTA provide the ``iota`` package, therefore, whenever you need
something from the library, you need to import it from there.

Notice, how we import the :py:class:`Iota` object, that defines a
so-called extended API object. We will use this to send and receive data from
the network. Read more about API objects at :ref:`PyOTA API Classes`.

We also import the ``pprint`` method that prettifies the output before printing
it to the console.

.. literalinclude:: ../examples/tutorials/01_hello_node.py
   :lines: 5-6
   :lineno-start: 5

Next, we declare an API object. Since this object handles the communication,
we need to specify an IOTA node to connect to in the form of an URI. Note, that
the library will parse this string and will throw an exception if it is not
a valid one.

.. literalinclude:: ../examples/tutorials/01_hello_node.py
   :lines: 8-9
   :lineno-start: 8

Then we can call the :py:meth:`Iota.get_node_info` method of the API
object to get some basic info about the node.

.. code-block::
    :lineno-start: 11

    # Using pprint instead of print for a nicer looking result in the console
    pprint(response)

Finally, we print out the response. It is important to note, that all API
methods return a python dictionary. Refer to the method's documentation to
determine what exactly is in the response ``dict``. Here for example,
we could list the ``features`` of the node::

    pprint(response['features'])

2. Send Data
------------
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
.. literalinclude:: ../examples/tutorials/02_send_data.py
   :lines: 1-5
   :lineno-start: 1

We have seen this part before. Note, that now we import more objects which we
will use to construct our transaction.

Notice ``testnet=True`` in the argument list of the API instantiation. We
tell the API directly that we will use the devnet/testnet. By default, the API
is configured for the mainnet.

.. literalinclude:: ../examples/tutorials/02_send_data.py
   :lines: 7-8
   :lineno-start: 7

If you read :ref:`Basic Concepts` and :ref:`PyOTA Types`, it shouldn't be a
surprise to you that most things in IOTA are represented as trytes, that are
:py:class:`TryteString` in PyOTA.

Here, we encode our message with :py:meth:`TryteString.from_unicode` into
trytes.

.. literalinclude:: ../examples/tutorials/02_send_data.py
   :lines: 10-11
   :lineno-start: 10

To put anything (transactions) on the Tangle, it needs to be associated with
an address. **Since we will be posting a zero-value transaction, nobody has to
own this address**; therefore we can use the :py:meth:`TryteString.random` (an
:py:class:`Address` is just a :py:class:`TryteString` with some additional
attributes and fixed length) method to generate one.

.. literalinclude:: ../examples/tutorials/02_send_data.py
   :lines: 13-14
   :lineno-start: 13

To tag our transaction, we might define a custom :py:class:`Tag` object.
Notice, that the ``b`` means we are passing a `bytestring`_ value instead of a
unicode string. This is so that PyOTA interprets our input as literal trytes,
rather than a unicode string that needs to be encoded into trytes.

When passing a bytestring to a PyOTA class, each byte is interpreted as a tryte;
therefore we are restricted to the `tryte alphabet`_.

.. literalinclude:: ../examples/tutorials/02_send_data.py
   :lines: 16-22
   :lineno-start: 16

It's time to construct the transaction. According to :ref:`Transaction Types`,
PyOTA uses :py:class:`ProposedTransaction` to build transactions that are not
yet broadcast to the network. Oberve, that the ``value=0`` means this is
a zero-value transaction.

.. literalinclude:: ../examples/tutorials/02_send_data.py
   :lines: 24-25
   :lineno-start: 24

Next, we send the transfer to the node for tip selection,
proof-of-work calculation, broadcasting and storing. The API takes care of
all these tasks, and returns the resulting ``Bundle`` object.

.. note::

    :py:meth:`~Iota.send_transfer` takes a list of :py:class:`ProposedTransaction`
    objects as its ``transfers`` argument. An IOTA transfer (bundle) usually
    consists of multiple transactions linked together, however, in this simple
    example, there is only one transaction in the bundle. Regardless, you need
    to pass this sole transaction as a list of one transaction.

.. literalinclude:: ../examples/tutorials/02_send_data.py
   :lines: 27-28
   :lineno-start: 27

Finally, we print out the transaction's link on the Tangle Explorer.
Observe how we extract the transaction hash from the response ``dict``. We take
the first element of the bundle, as it is just a sequence of transactions, and
access its ``hash`` attribute.

3. Fetch Data
-------------
In this example, you will learn how to:

- **Fetch transaction objects from the Tangle based on a criteria.**
- **Decode messages from transactions.**

Code
~~~~
.. literalinclude:: ../examples/tutorials/03_fetch_data.py
   :linenos:

Discussion
~~~~~~~~~~
.. literalinclude:: ../examples/tutorials/03_fetch_data.py
   :lines: 1-5
   :lineno-start: 1

The usual part again, but we also import ``TrytesDecodeError`` from
``iota.codec``. We will use this to detect if the fetched trytes contain
encoded text.

.. literalinclude:: ../examples/tutorials/03_fetch_data.py
   :lines: 7-10
   :lineno-start: 7

We declare an IOTA address on the Tangle to fetch data from. You can replace
this address with your own from the previous example `2. Send Data`_, or just
run it as it is.

.. literalinclude:: ../examples/tutorials/03_fetch_data.py
   :lines: 12-14
   :lineno-start: 12

We use :py:meth:`~Iota.find_transaction_objects` extended API method to gather
the transactions that belong to our address. This method is also capable of
returning :py:class:`Transaction` objects for bundle hashes, tags or approving
transactions. Note that you can supply multiple of these, the method always
returns a ``dict`` with a list of transactions.

.. note::

    Remember, that the parameters need to be supplied as lists, even if
    there is only one value.

.. literalinclude:: ../examples/tutorials/03_fetch_data.py
   :lines: 16-25
   :lineno-start: 16

Finally, we extract the data we are looking for from the transaction objects.
A :py:class:`Transaction` has several attributes, one of which is the
``signature_message_fragment``. This contains the payload message for zero-value
transactions, and the digital signature that authorizes spending for value
transactions.

Since we are interested in data now, we decode its content (raw trytes) into
text. Notice, that we pass the ``errors='ignore'`` argument to the ``decode()``
method to drop values we can't decode using ``utf-8``, or if the raw trytes
can't be decoded into legit bytes. A possible reason for the latter can be if
the attribute contains a signature rather than a message.

.. _PyOTA Bug Tracker: https://github.com/iotaledger/iota.py/issues
.. _bytestring: https://docs.python.org/3/library/stdtypes.html#bytes
.. _tryte alphabet: https://docs.iota.org/docs/getting-started/0.1/introduction/ternary#tryte-encoding
.. _Tangle Explorer: https://utils.iota.org