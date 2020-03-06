PyOTA Types
===========

PyOTA defines a few types that will make it easy for you to model
objects like Transactions and Bundles in your own code.

Since everything in IOTA is represented as a sequence of ``trits`` and ``trytes``,
let us take a look on how you can work with them in PyOTA.

TryteString
-----------
.. py:currentmodule:: iota

.. autoclass:: TryteString

Example usage:

.. code:: python

    from iota import TryteString

    # Create a TryteString object from bytes.
    trytes_1 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    # Ensure the created object is 81 trytes long by padding it with zeros.
    # The value zero is represented with character '9' in trytes.
    trytes_1 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA', pad=81)

    # Create a TryteString object from text type.
    # Note that this will throw error if text contains unsupported characters.
    trytes_2 = TryteString('LH9GYEMHCF9GWHZFEELHVFOEOHNEEEWHZFUD')

    # Comparison and concatenation:
    if trytes_1 != trytes_2:
      trytes_combined = trytes_1 + trytes_2

    # As dictionary keys:
    index = {
      trytes_1: 42,
      trytes_2: 86,
    }

As you go through the API documentation, you will see many references to
:py:class:`TryteString` and its subclasses:

-  :py:class:`Fragment`: A signature or message fragment inside a transaction.
   Fragments are always 2187 trytes long.
-  :py:class:`Hash`: An object identifier. Hashes are always 81 trytes long.
   There are many different types of hashes:
-  :py:class:`Address`: Identifies an address on the Tangle.
-  :py:class:`BundleHash`: Identifies a bundle on the Tangle.
-  :py:class:`TransactionHash`: Identifies a transaction on the Tangle.
-  :py:class:`Seed`: A TryteString that is used for crypto functions such as
   generating addresses, signing inputs, etc. Seeds can be any length,
   but 81 trytes offers the best security.
-  :py:class:`Tag`: A tag used to classify a transaction. Tags are always 27
   trytes long.
-  :py:class:`TransactionTrytes`: A TryteString representation of a transaction
   on the Tangle. ``TransactionTrytes`` are always 2673 trytes long.

Let's explore the capabilities of the :py:class:`TryteString` base class.

Encoding
~~~~~~~~

You may use classmethods to create a :py:class:`TryteString` from ``bytes``,
``unicode string`` or from a list of ``trits``.

**from_bytes**
^^^^^^^^^^^^^^
.. automethod:: TryteString.from_bytes

**from_unicode**
^^^^^^^^^^^^^^^^
.. automethod:: TryteString.from_unicode

.. note::

    PyOTA also supports encoding non-ASCII characters, but this functionality is
    **experimental** and has not yet been evaluated by the IOTA
    community!

    Until this feature has been standardized, it is recommended that you only
    use ASCII characters when generating ``TryteString`` objects from
    character strings.

**from_trits**
^^^^^^^^^^^^^^
.. automethod:: TryteString.from_trits

**from_trytes**
^^^^^^^^^^^^^^^
.. automethod:: TryteString.from_trytes

Additionally, you can encode a :py:class:`TryteString` into a lower-level
primitive (usually bytes). This might be useful when the :py:class:`TryteString`
contains ASCII encoded characters but you need it as ``bytes``. See the example
below:

**encode**
^^^^^^^^^^
.. automethod:: TryteString.encode


Decoding
~~~~~~~~

You can also convert a tryte sequence into characters using
:py:meth:`TryteString.decode`. Note that not every tryte sequence can be
converted; garbage in, garbage out!

**decode**
^^^^^^^^^^
.. automethod:: TryteString.decode

**as_json_compatible**
^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: TryteString.as_json_compatible

**as_integers**
^^^^^^^^^^^^^^^
.. automethod:: TryteString.as_integers

**as_trytes**
^^^^^^^^^^^^^
.. automethod:: TryteString.as_trytes

**as_trits**
^^^^^^^^^^^^
.. automethod:: TryteString.as_trits

Generation
~~~~~~~~~~

**random**
^^^^^^^^^^
.. automethod:: TryteString.random

Seed
----
.. autoclass:: Seed

**random**
~~~~~~~~~~
.. automethod:: Seed.random

Address
-------
.. autoclass:: Address
  :members: address, balance, key_index, security_level

**as_json_compatible**
~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: Address.as_json_compatible

**is_checksum_valid**
~~~~~~~~~~~~~~~~~~~~~
.. automethod:: Address.is_checksum_valid

**with_valid_checksum**
~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: Address.with_valid_checksum

**add_checksum**
~~~~~~~~~~~~~~~~
.. automethod:: Address.add_checksum

**remove_checksum**
~~~~~~~~~~~~~~~~~~~
.. automethod:: Address.remove_checksum

AddressChecksum
---------------
.. autoclass:: AddressChecksum
  :members:

Hash
----
.. autoclass:: Hash
  :members:

TransactionHash
---------------
.. autoclass:: TransactionHash
  :members:

BundleHash
----------
.. autoclass:: BundleHash
  :members:

TransactionTrytes
-----------------
.. autoclass:: TransactionTrytes
  :members:

Fragment
--------
.. autoclass:: Fragment
  :members:

Nonce
-----
.. autoclass:: Nonce
  :members:

Tag
---
.. autoclass:: Tag
  :members:

Transaction Types
-----------------

PyOTA defines two different types used to represent transactions:

 - :py:class:`Transaction` for transactions that have already been
   attached to the Tangle. Generally, you will never need to create
   :py:class:`Transaction` objects; the API will build them for you,
   as the result of various API methods.
 - :py:class:`ProposedTransaction` for transactions that have been created
   locally and have not been broadcast yet.

Transaction
~~~~~~~~~~~
Each :py:class:`Transaction` object has several instance attributes that you
may manipulate and properties you can use to extract their values as trytes.
See the class documentation below:

.. autoclass:: Transaction
  :members: hash, bundle_hash, address, value, nonce, timestamp,
    current_index, last_index, trunk_transaction_hash, branch_transaction_hash,
    tag, attachment_timestamp, attachment_timestamp_lower_bound,
    attachment_timestamp_upper_bound, signature_message_fragment, is_confirmed,
    is_tail, value_as_trytes, timestamp_as_trytes, current_index_as_trytes,
    last_index_as_trytes, attachment_timestamp_as_trytes,
    attachment_timestamp_lower_bound_as_trytes,
    attachment_timestamp_upper_bound_as_trytes, legacy_tag

**as_json_compatible**
^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: Transaction.as_json_compatible

**as_tryte_string**
^^^^^^^^^^^^^^^^^^^
.. automethod:: Transaction.as_tryte_string

**from_tryte_string**
^^^^^^^^^^^^^^^^^^^^^
.. automethod:: Transaction.from_tryte_string

**get_bundle_essence_trytes**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: Transaction.get_bundle_essence_trytes

ProposedTransaction
~~~~~~~~~~~~~~~~~~~

.. autoclass:: ProposedTransaction

**as_tryte_string**
^^^^^^^^^^^^^^^^^^^
.. automethod:: ProposedTransaction.as_tryte_string

**increment_legacy_tag**
^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: ProposedTransaction.increment_legacy_tag

Bundle Types
------------

As with transactions, PyOTA defines two different types to represent bundles:

 - :py:class:`Bundle` for bundles that have already been
   broadcast to the Tangle. Generally, you will never need to create
   :py:class:`Bundle` objects; the API will build them for you,
   as the result of various API methods.
 - :py:class:`ProposedBundle` for bundles that have been created
   locally and have not been broadcast yet.

Bundle
~~~~~~

.. autoclass:: Bundle
  :members: is_confirmed, hash, tail_transaction, transactions

**as_json_compatible**
^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: Bundle.as_json_compatible

**as_tryte_strings**
^^^^^^^^^^^^^^^^^^^^
.. automethod:: Bundle.as_tryte_strings

**from_tryte_strings**
^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: Bundle.from_tryte_strings

**get_messages**
^^^^^^^^^^^^^^^^
.. automethod:: Bundle.get_messages

**group_transactions**
^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: Bundle.group_transactions

ProposedBundle
~~~~~~~~~~~~~~
.. note::
  This section contains information about how PyOTA works "under the
  hood".

  The :py:meth:`Iota.prepare_transfer` API method encapsulates this
  functionality for you; it is not necessary to understand how
  :py:class:`ProposedBundle` works in order to use PyOTA.

.. autoclass:: ProposedBundle
  :members: balance, tag

:py:class:`ProposedBundle` provides a convenient interface for creating new
bundles, listed in the order that they should be invoked:

**add_transaction**
^^^^^^^^^^^^^^^^^^^
.. automethod:: ProposedBundle.add_transaction

**add_inputs**
^^^^^^^^^^^^^^
.. automethod:: ProposedBundle.add_inputs

**send_unspent_inputs_to**
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: ProposedBundle.send_unspent_inputs_to

**add_signature_or_message**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: ProposedBundle.add_signature_or_message

**finalize**
^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: ProposedBundle.finalize

**sign_inputs**
^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: ProposedBundle.sign_inputs

**sign_input_at**
^^^^^^^^^^^^^^^^^
.. automethod:: ProposedBundle.sign_input_at

**as_json_compatible**
^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: ProposedBundle.as_json_compatible

**Example usage**
^^^^^^^^^^^^^^^^^

.. code:: python

    from iota import Address, ProposedBundle, ProposedTransaction
    from iota.crypto.signing import KeyGenerator

    bundle = ProposedBundle()

    bundle.add_transaction(ProposedTransaction(...))
    bundle.add_transaction(ProposedTransaction(...))
    bundle.add_transaction(ProposedTransaction(...))

    bundle.add_inputs([
      Address(
        address =
          b'TESTVALUE9DONTUSEINPRODUCTION99999HAA9UA'
          b'MHCGKEUGYFUBIARAXBFASGLCHCBEVGTBDCSAEBTBM',

        balance   = 86,
        key_index = 0,
      ),
    ])

    bundle.send_unspent_inputs_to(
      Address(
        b'TESTVALUE9DONTUSEINPRODUCTION99999D99HEA'
        b'M9XADCPFJDFANCIHR9OBDHTAGGE9TGCI9EO9ZCRBN'
      ),
    )

    bundle.finalize()
    bundle.sign_inputs(KeyGenerator(b'SEED9GOES9HERE'))

Once the :py:class:`ProposedBundle` has been finalized (and inputs signed, if
necessary), invoke its :py:meth:`ProposedBundle.as_tryte_strings` method to
generate the raw trytes that should be included in an
:py:meth:`Iota.attach_to_tangle` API request.
