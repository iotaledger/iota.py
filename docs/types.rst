================
PyOTA Data Types
================
.. important::

   Before diving into the API, it's important to understand the fundamental data
   types of IOTA.

   For an introduction to the IOTA protocol and the Tangle, give the
   `protocol documentation`_ a once-over.

PyOTA defines a few types that will make it easy for you to model objects like
Transactions and Bundles in your own code.

TryteString
-----------
A :py:class:`TryteString` is an ASCII representation of a sequence of trytes.
In many respects, it is similar to a Python ``bytes`` object (which is an ASCII
representation of a sequence of bytes).

In fact, the two objects behave very similarly; they support concatenation,
comparison, can be used as dict keys, etc.

However, unlike ``bytes``,  a :py:class:`TryteString` can only contain uppercase
letters and the number 9 (as a regular expression: ``^[A-Z9]*$``).

.. admonition:: Why only these characters?

   You can find the answer on the
   `IOTA Forum <https://forum.iota.org/t/1860/10>`__.

As you go through the API documentation, you will see many references to
:py:class:`TryteString` and its subclasses:

- :py:class:`Fragment`

  A signature or message fragment inside a transaction.
  Fragments are always 2187 trytes long.

- :py:class:`Hash`

  An object identifier.  Hashes are always 81 trytes long.

  There are many different types of hashes:

   :py:class:`Address`
      Identifies an address on the Tangle.
   :py:class:`BundleHash`
      Identifies a bundle on the Tangle.
   :py:class:`TransactionHash`
      Identifies a transaction on the Tangle.

- :py:class:`Seed`

  A TryteString that is used for crypto functions such as generating addresses,
  signing inputs, etc.

  .. important::

     Seeds can be any length, but 81 trytes offers the best security.
     More information is available on the
     `IOTA Forum <https://forum.iota.org/t/1278>`__.

- :py:class:`Tag`

  A tag used to classify a transaction.  Tags are always 27 trytes long.

- :py:class:`TransactionTrytes`

  A TryteString representation of a transaction on the Tangle.
  :py:class:`TransactionTrytes` are always 2673 trytes long.

Creating TryteStrings
~~~~~~~~~~~~~~~~~~~~~
To create a new :py:class:`TryteString` from a sequence of trytes, simply
wrap the trytes inside the :py:class:`TryteString` initializer:

.. code-block:: python

   from iota import TryteString

   trytes = TryteString('RBTC9D9DCDQAEASBYBCCKBFA')

To encode ASCII text into trytes, use the :py:meth:`TryteString.from_string`
method:

.. code-block:: python

   from iota import TryteString

   message_trytes = TryteString.from_string('Hello, IOTA!')

   print(message_trytes) # RBTC9D9DCDQAEASBYBCCKBFA

To decode a sequence of trytes back into ASCII text, use
:py:meth:`TryteString.as_string`:

.. code-block:: python

   from iota import TryteString

   message_trytes = TryteString('RBTC9D9DCDQAEASBYBCCKBFA')

   message_str = message_trytes.as_string()

   print(message_str) # Hello, IOTA!

.. note::

   PyOTA also supports encoding non-ASCII characters, but this functionality is
   **experimental** and has not yet been standardized.

   If you encode non-ASCII characters, be aware that other IOTA libraries
   (possibly including future versions of PyOTA!) might not be able to decode
   them!

Transaction Types
-----------------
PyOTA defines two different types used to represent transactions:

:py:class:`Transaction`
   A transaction that has been loaded from the Tangle.

:py:class:`ProposedTransaction`
   A transaction that was created locally and hasn't been broadcast to the
   Tangle yet.

Transaction
~~~~~~~~~~~
Generally, you will never need to create `Transaction` objects; the API will
build them for you, as the result of various API methods.

.. tip::

   If you have a TryteString representation of a transaction, and you'd like to
   convert it into a :py:class:`Transaction` object, use the
   :py:meth:`Transaction.from_tryte_string` method:

   .. code-block:: python

      from iota import Transaction

      txn_1 =\
        Transaction.from_tryte_string(
          'GYPRVHBEZOOFXSHQBLCYW9ICTCISLHDBNMMVYD9JJHQMPQCTIQ...',
        )

   This is equivalent to the `Paste Trytes`_ feature from the IOTA Wallet.

Each :py:class:`Transaction` object has the following attributes:

- ``address`` (:py:class:`Address`)

   The address associated with this transaction.  Depending on the transaction's
   ``value``, this address may be a sender or a recipient.

- ``attachment_timestamp`` (:py:class:`int`)
  Timestamp after completing the Proof of Work process.

  See the `timestamps white paper`_ for more information.

- ``attachment_timestamp_lower_bound`` (:py:class:`int`)
  Lower bound of the timestamp.

  See the `timestamps white paper`_ for more information.

- ``attachment_timestamp_upper_bound`` (:py:class:`int`)
  Upper bound of the timestamp.

  See the `timestamps white paper`_ for more information.

- ``branch_transaction_hash`` (:py:class:`TransactionHash`)

  An unrelated transaction that this transaction "approves".
  Refer to the `protocol documentation`_ for more information.

- ``bundle_hash`` (:py:class:`BundleHash`)

   The bundle hash, used to identify transactions that are part of the same
   bundle.  This value is generated by taking a hash of the metadata from all
   transactions in the bundle.

- ``current_index`` (:py:class:`int`)

   The transaction's position in the bundle.

   - If the ``current_index`` value is 0, then this is the "tail transaction".
   - If it is equal to ``last_index``, then this is the "head transaction".

- ``hash`` (:py:class:`TransactionHash`)

   The transaction hash, used to uniquely identify the transaction on the
   Tangle.  This value is generated by taking a hash of the raw transaction
   trytes.

- ``last_index`` (:py:class:`int`)

   The index of the final transaction in the bundle.  This value is attached to
   every transaction to make it easier to traverse and verify bundles.

- ``nonce`` (:py:class:`Nonce`)

   This is the product of the PoW process.

   Refer to the `protocol documentation`_ for more information.

- ``signature_message_fragment`` (:py:class:`Fragment`)

   Additional data attached to the transaction:

   - If ``value < 0``, this value contains a fragment of the cryptographic
     signature authorizing the spending of the IOTAs.
   - If ``value > 0``, this value is an (optional) string message attached to
     the transaction.
   - If ``value = 0``, this value could be either a signature or message
     fragment, depending on the previous transaction.

   .. tip::

      Read this as "Signature/Message Fragment".  That is, it could be a
      fragment of a signature **or** a message, depending on the transaction.

- ``tag`` (:py:class:`Tag`)

   Used to classify the transaction.

   Every transaction has a tag, but many transactions have empty tags.

- ``timestamp`` (:py:class:`int`)

  Unix timestamp when the transaction was created.

  Note that devices can specify any timestamp when creating transactions, so
  this value is not safe to use by itself for security measures (such as
  resolving double-spends).

  .. note::

     The IOTA protocol does support verifiable timestamps.  Refer to the
     `timestamps white paper`_ for more information.

- ``trunk_transaction_hash`` (:py:class:`TransactionHash`)

   The transaction hash of the next transaction in the bundle.

   If this transaction is the head transaction, its ``trunk_transaction_hash``
   will be pseudo-randomly selected, similarly to ``branch_transaction_hash``.

- ``value`` (:py:class:`int`)

   The number of IOTAs being transferred in this transaction:

  - If this value is negative, then the ``address`` is spending IOTAs.
  - If it is positive, then the ``address`` is receiving IOTAs.
  - If it is zero, then this transaction is being used to carry metadata (such
    as a signature fragment or a message) instead of transferring IOTAs.


:todo: ProposedTransaction


.. _protocol documentation: https://iota.readme.io/docs/
.. _paste trytes: https://forum.iota.org/t/3457/3
.. _timestamps white paper: https://iota.org/timestamps.pdf
