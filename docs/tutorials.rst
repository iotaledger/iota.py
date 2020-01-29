Tutorials
=========
Are you new to IOTA in Python? Don't worry, we got you covered! With the
walkthrough examples of this section, you will be a master of PyOTA.

In each section below, a code snippet will be shown and discussed in detail
to help you understand how to carry out specific tasks with PyOTA.

The example scripts displayed here can also be found under ``examples/tutorials/``
directory in the repository. Run them in a Python environment that has PyOTA
installed. See :ref:`Install PyOTA` for more info.

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

Notice ``devnet=True`` in the argument list of the API instantiation. We
tell the API directly that we will use IOTA's testnet, known as the devnet.
By default, the API is configured for the mainnet.

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

4.a Generate Address
--------------------

In this example, you will learn how to:

- **Generate a random seed.**
- **Generate an IOTA address that belongs to your seed.**
- **Acquire free devnet IOTA tokens that you can use to play around with.**

Code
~~~~
.. literalinclude:: ../examples/tutorials/04a_gen_address.py
   :linenos:

Discussion
~~~~~~~~~~
.. literalinclude:: ../examples/tutorials/04a_gen_address.py
   :lines: 1-7
   :lineno-start: 1

We start off by generating a random seed with the help of the library. You are
also free to use your own seed, just uncomment line 6 and put it there.

If you choose to generate one, your seed is written to the console so that you
can save it for later. Be prepared to do so, because you will have to use it
in the following tutorials.

.. literalinclude:: ../examples/tutorials/04a_gen_address.py
   :lines: 9-14
   :lineno-start: 9

Notice, how we pass the ``seed`` argument to the API class's init method.
Whenever the API needs to work with addresses or private keys, it will derive
them from this seed.

.. important::

    Your seed never leaves the library and your computer. Treat your (mainnet)
    seed like any other password for a financial service: safe. If your seed is
    compromised, attackers can steal your funds.

.. literalinclude:: ../examples/tutorials/04a_gen_address.py
   :lines: 16-20
   :lineno-start: 16

To generate a new address, we call :py:meth:`~Iota.get_new_addresses`
extended API method. Without arguments, this will return a ``dict`` with the
first unused address starting from ``index`` 0. An unused address is address
that has no transactions referencing it on the Tangle and was never spent from.

If we were to generate more addresses starting from a desired index,
we could specify the ``start`` and ``count`` parameters. Read more about how to
generate addresses in PyOTA at :ref:`Generating Addresses`.

On line 20 we access the first element of the list of addresses in the response
dictionary.

.. literalinclude:: ../examples/tutorials/04a_gen_address.py
   :lines: 22-23
   :lineno-start: 22

Lastly, the address is printed to the console, so that you can copy it.
Visit https://faucet.devnet.iota.org/ and enter the address to receive free
devnet tokens of 1000i.

You might need to wait 1-2 minutes until the sum arrives to you address. To
check your balance, go to `4.b Check Balance`_ or `4.c Get Account Data`_.

4.b Check Balance
-----------------

In this example, you will learn how to:

- **Check the balance of a specific IOTA address.**

Code
~~~~
.. literalinclude:: ../examples/tutorials/04b_check_balance.py
   :linenos:

Discussion
~~~~~~~~~~
.. literalinclude:: ../examples/tutorials/04b_check_balance.py
   :lines: 1-8
   :lineno-start: 1

The first step  to check the balance of an address is to actually have an
address. Exchange the sample address on line 5 with your generated address from
`4.a Generate Address`_.

Since we don't need to generate an address, there is no need for a seed to be
employed in the API object. Note the ``time`` import, we need it for later.

.. literalinclude:: ../examples/tutorials/04b_check_balance.py
   :lines: 10-25
   :lineno-start: 10

Our script will poll the network for the address balance as long as the returned
balance is zero. Therefore, the address you declared as ``my_address`` should
have some balance. If you see the ``Zero balance found...`` message a couple of
times, head over to https://faucet.devnet.iota.org/ and load up your address.

:py:meth:`~Iota.get_balances` returns the confirmed balance of the address.
You could supply multiple addresses at the same time and get their respective
balances in a single call. Don't forget, that the method returns a ``dict``.
More details about it can be found at :py:meth:`~Iota.get_balances`.

4.c Get Account Data
--------------------

In this example, you will learn how to:

- **Gather addresses, balance and bundles associated with your seed on the Tangle.**

.. warning::

    **Account** in the context of this example is not to be confused with the
    `Account Module`_, that is a feature yet to be implemented in PyOTA.

    **Account** here simply means the addresses and funds that belong to your
    seed.

Code
~~~~
.. literalinclude:: ../examples/tutorials/04c_get_acc_data.py
   :linenos:

Discussion
~~~~~~~~~~
.. literalinclude:: ../examples/tutorials/04c_get_acc_data.py
   :lines: 1-3
   :lineno-start: 1

We will need ``pprint`` for a prettified output of the response ``dict`` and
``time`` for polling until we find non-zero balance.

.. literalinclude:: ../examples/tutorials/04c_get_acc_data.py
   :lines: 5-13
   :lineno-start: 5

Copy your seed from `4.a Generate Address`_ onto line 6. The API will use your
seed to generate addresses and look for corresponding transactions on the
Tangle.

.. literalinclude:: ../examples/tutorials/04c_get_acc_data.py
   :lines: 15-30
   :lineno-start: 15

Just like in the previous example, we will poll for information until we find
a non-zero balance. :py:meth:`~Iota.get_account_data` without arguments
generates addresses from ``index`` 0 until it finds the first unused. Then, it
queries the node about bundles of those addresses and sums up their balance.

.. note::

    If you read :py:meth:`~Iota.get_account_data` documentation carefully, you
    notice that you can gain control over which addresses are checked during
    the call by specifying the ``start`` and ``stop`` index parameters.

    This can be useful when your addresses with funds do not follow each other
    in the address namespace, or a snapshot removed transactions from the
    Tangle. It is recommended that you keep a local database of your already
    used address indices.

    Once implemented in PyOTA, `Account Module`_ will address the aforementioned
    problems.

The response ``dict`` contains the addresses, bundles and total balance of
your seed.

5. Send Tokens
--------------

In this example, you will learn how to:

- **Construct a value transfer with PyOTA.**
- **Send a value transfer to an arbitrary IOTA address.**
- **Analyze a bundle of transactions on the Tangle.**

.. note::

    As a prerequisite to this tutorial, you need to have completed
    `4.a Generate Address`_, and have a seed that owns devnet tokens.

Code
~~~~
.. literalinclude:: ../examples/tutorials/05_send_tokens.py
   :linenos:

Discussion
~~~~~~~~~~
.. literalinclude:: ../examples/tutorials/05_send_tokens.py
   :lines: 1-11
   :lineno-start: 1

We are going to send a value transaction, that requires us to prove that we
own the address containg the funds to spend. Therefore, we need our seed from
which the address was generated.

Put your seed from `4.a Generate Address`_ onto line 4. We pass this seed to
the API object, that will utilize it for signing the transfer.

.. literalinclude:: ../examples/tutorials/05_send_tokens.py
   :lines: 13-16
   :lineno-start: 13

In IOTA, funds move accross addresses, therefore we need to define a **receiver
address**. For testing value transfers, you should send the funds only to
addresses that you control; if you use a randomly-generated receiver address,
you won't be able to recover the funds afterward!
Re-run `4.a Generate Address`_ for a new seed and a new address, or just paste
a valid IOTA address that you own onto line 16.

.. literalinclude:: ../examples/tutorials/05_send_tokens.py
   :lines: 18-25
   :lineno-start: 18

We declare a :py:class:`ProposedTransaction` object like we did before, but
this time, with ``value=1`` parameter. The smallest value you can send is 1
iota ("1i"), there is no way to break it into smaller chunks. It is a really small
value anyway. You can also attach a message to the transaction, for example a
little note to the beneficiary of the payment.

.. literalinclude:: ../examples/tutorials/05_send_tokens.py
   :lines: 27-29
   :lineno-start: 27

To actually send the transfer, all you need to do is call
:py:meth:`~Iota.send_transfer` extended API method. This method will take care
of:

- Gathering ``inputs`` (addresses you own and have funds) to fund the 1i transfer.
- Generating a new ``change_address``, and automatically sending the remaining
  funds (``balance of chosen inputs`` - 1i) from ``inputs`` to ``change_address``.

    .. warning::

        This step is extremely important, as it prevents you from `spending twice
        from the same address`_.

        When an address is used as an input, all tokens will be withdrawn. Part
        of the tokens will be used to fund your transaction, the rest will be
        transferred to ``change_address``.

- Constructing the transfer bundle with necessary input and output transactions.
- Finalizing the bundle and signing the spending transactions.
- Doing proof-of-work for each transaction in the bundle and sending it to the
  network.

.. literalinclude:: ../examples/tutorials/05_send_tokens.py
   :lines: 31-32
   :lineno-start: 31

Open the link and observe the bundle you have just sent to the Tangle. Probably
it will take a couple of seconds for the network to confirm it.

What you see is a bundle with 4 transactions in total, 1 input and 3 outputs.
But why are there so many transactions?

- There is one transaction that withdraws iotas, this has negative value.
  To authorize this spending, a valid signature is included in the transaction's
  ``signature_message_fragment`` field. The signature however is too long to
  fit into one transaction, therefore the library appends a new, zero-value
  transaction to the bundle that holds the second part of the signature. This
  you see on the output side of the bundle.
- A 1i transaction to the receiver address spends part of the withdrawn amount.
- The rest is transfered to ``change_address`` in a new output transaction.

Once the bundle is confirmed, try rerunning the script from
`4.c Get Account Data`_ with the same seed as in this tutorial. Your balance
should be decremented by 1i, and you should see a new address, which was
actually the ``change_address``.

6. Store Encrypted Data
-----------------------

In this example, you will learn how to:

- **Convert Python data structures to JSON format.**
- **Encrypt data and include it in a zero-value transaction.**
- **Store the zero-value transaction with encrypted data on the Tangle.**

.. warning::

    We will use the ``simple-crypt`` external library for encryption/decryption.
    Before proceeding to the tutorial, make sure you install it by running::

        pip install simple-crypt

Code
~~~~
.. literalinclude:: ../examples/tutorials/06_store_encrypted.py
   :linenos:

Discussion
~~~~~~~~~~
.. literalinclude:: ../examples/tutorials/06_store_encrypted.py
   :lines: 1-18
   :lineno-start: 1

We will use the ``encrypt`` method to encipher the data, and ``b64encode`` for
representing it as ASCII characters. ``getpass`` will prompt the user for a
password, and the ``json`` library is used for JSON formatting.

We will need an address to upload the data, therefore we need to supply the
seed to the ``Iota`` API instance. The address will be generated from this
seed.

.. literalinclude:: ../examples/tutorials/06_store_encrypted.py
   :lines: 20-26
   :lineno-start: 20

The data to be stored is considered confidential information, therefore we
can't just put it on the Tangle as plaintext so everyone can read it. Think of
what would happen if the world's most famous secret agent's identity was leaked
on the Tangle...

.. literalinclude:: ../examples/tutorials/06_store_encrypted.py
   :lines: 28-29
   :lineno-start: 28

Notice, that ``data`` is a Python ``dict`` object. As a common way of exchanging
data on the web, we would like to convert it to JSON format. The ``json.dumps()``
method does exactly that, and the result is a JSON formatted plaintext.

.. literalinclude:: ../examples/tutorials/06_store_encrypted.py
   :lines: 31-40
   :lineno-start: 31

Next, we will encrypt this data with a secret password we obtain from the user.

.. note::

    When you run this example, please remember the password at least until the
    next tutorial!

The output of the ``encrypt`` method is a ``bytes`` object in Python3 and
contains many special characters. This is a problem, since we can only convert
ASCII characters from ``bytes`` directly into :py:class:`TryteString`.

Therefore, we first encode our binary data into ASCII characters with `Base64`_
encoding.

.. literalinclude:: ../examples/tutorials/06_store_encrypted.py
   :lines: 42-58
   :lineno-start: 42

Now, we are ready to construct the transfer. We convert the encrypted `Base64`_
encoded data to trytes and assign it to the :py:class:`ProposedTransaction`
object's ``message`` argument.

An address is also needed, so we generate one with the help of
:py:meth:`~Iota.get_new_addresses` extended API method. Feel free to choose the
index of the generated address, and don't forget, that the method returns a
``dict`` with a list of addresses, even if it contains only one.
For more detailed explanation on how addresses are generated in PyOTA,
refer to the :ref:`Generating Addresses` page.

We also attach a custom :py:class:`Tag` to our :py:class:`ProposedTransaction`.
Note, that if our ``trytes_encrypted_data`` was longer than the maximum payload
of a transaction, the library would split it accross more transactions that
together form the transfer bundle.

.. literalinclude:: ../examples/tutorials/06_store_encrypted.py
   :lines: 60-66
   :lineno-start: 60

Finally, we use :py:meth:`Iota.send_transfer` to prepare the transfer and
send it to the network.

Click on the link to check your transaction on the Tangle Explorer.

The tail transaction (a tail transaction is the one with index 0 in the bundle)
hash is printed on the console, because you will need it in the next tutorial,
and anyway, it is a good practice to keep a reference to your transfers.

In the next example, we will try to decode the confidential information from
the Tangle.

7. Fetch Encrypted Data
-----------------------

In this example, you will learn how to:

- **Fetch bundles from the Tangle based on their tail transaction hashes.**
- **Extract messages from a bundle.**
- **Decrypt encrypted messages from a bundle.**

.. warning::

    We will use the ``simple-crypt`` external library for encryption/decryption.
    Before proceeding to the tutorial, make sure you install it by running::

        pip install simple-crypt

Code
~~~~
.. literalinclude:: ../examples/tutorials/07_fetch_encrypted.py
   :linenos:

Discussion
~~~~~~~~~~
.. literalinclude:: ../examples/tutorials/07_fetch_encrypted.py
   :lines: 1-14
   :lineno-start: 1

In contrast to `6. Store Encrypted Data`_ where we intended to encrypt data, in
this tutorial we will do the reverse, and decrypt data from the Tangle.
Therefore, we need the ``decrypt`` method from ``simplecrypt`` library and the
``b64decode`` method from ``base64`` library.

Furthermore, ``getpass`` is needed to prompt the user for a decryption
password, and ``json`` for deserializing JSON formatted string into Python
object.

.. literalinclude:: ../examples/tutorials/07_fetch_encrypted.py
   :lines: 16-17
   :lineno-start: 16

To fetch transactions or bundles from the Tangle, a reference is required to
retreive them from the network. Transactions are identified by their
transaction hash, while a group of transaction (a bundle) by bundle hash.
Hashes ensure the integrity of the Tangle, since they contain verifiable
information about the content of the transfer objects.

``input()`` asks the user to give the tail transaction hash of the bundle
that holds the encrypted messages. The tail transaction is the first in the
bundle with index 0. Copy and paste the tail transaction hash from the console
output of `6. Store Encrypted Data`_ when prompted.

.. literalinclude:: ../examples/tutorials/07_fetch_encrypted.py
   :lines: 19-21
   :lineno-start: 19

Next, we fetch the bundle from the Tangle with the help of the
:py:meth:`~Iota.get_bundles` extended API command. It takes a list of tail
transaction hashes and returns the bundles for each of them. The response
``dict`` contains a ``bundles`` key with the value being a list of bundles
in the same order as the input argument hashes. Also note, that the bundles
in the response are actual PyOTA :py:class:`Bundle` objects.

To simplify the code, several operations are happening on line 21:

- Calling :py:meth:`~Iota.get_bundles` that returns a ``dict``,
- accessing the ``'bundles'`` key in the ``dict``,
- and taking the first element of the the list of bundles in the value
  associated with the key.

.. literalinclude:: ../examples/tutorials/07_fetch_encrypted.py
   :lines: 23-39
   :lineno-start: 23

The next step is to extract the content of the message fields of the
transactions in the bundle. We call :py:meth:`Bundle.get_messages` to carry
out this operation. The method returns a list of unicode strings, essentially
the ``signature_message_fragment`` fields of the transactions, decoded from
trytes into unicode characters.

We then combine these message chunks into one stream of characters by using
``string.join()``.

We know that at this stage that we can't make sense of our message, because it
is encrypted and encoded into `Base64`_. Let's peel that onion layer by layer:

- On line 28, we decode the message into bytes with ``b64decode``.
- On line 31, we ask the user for thr decryption password (from the previous
  tutorial).
- On line 36, we decrypt the bytes cipher with the password and decode the
  result into a unicode string.
- Since we used JSON formatting in the previous tutorial, there is one
  additional step to arrive at our original data. On line 39, we deserialize
  the JSON string into a Python object, namely a ``dict``.

.. literalinclude:: ../examples/tutorials/07_fetch_encrypted.py
   :lines: 41-42
   :lineno-start: 41

If everything went according to plan and the user supplied the right password,
we should see our original data printed out to the console.

Now you know how to use the Tangle for data storage while keeping privacy.
When you need more granular access control on how and when one could read
data from the Tangle, consider using `Masked Authenticated Messaging`_ (MAM).

.. _PyOTA Bug Tracker: https://github.com/iotaledger/iota.py/issues
.. _bytestring: https://docs.python.org/3/library/stdtypes.html#bytes
.. _tryte alphabet: https://docs.iota.org/docs/getting-started/0.1/introduction/ternary#tryte-encoding
.. _Tangle Explorer: https://utils.iota.org
.. _Account Module: https://docs.iota.org/docs/client-libraries/0.1/account-module/introduction/overview
.. _spending twice from the same address: https://docs.iota.org/docs/getting-started/0.1/clients/addresses#spent-addresses
.. _Base64: https://en.wikipedia.org/wiki/Base64
.. _Masked Authenticated Messaging: https://docs.iota.org/docs/client-libraries/0.1/mam/introduction/overview?q=masked%20auth&highlights=author;authent