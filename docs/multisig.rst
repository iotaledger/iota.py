Multisignature
==============

Multisignature transactions are transactions which require multiple signatures
before execution. In simplest example it means that, if there is token wallet
which require 5 signatures from different parties, all 5 parties must sign spent
transaction, before it will be processed.

It is standard functionality in blockchain systems and it is also implemented
in IOTA.

.. note::

    You can read more about IOTA multisignature on the `wiki`_.

First, we will take a look on what `Multisig API`_ (s) you can use, and what
`PyOTA Multisignature Types`_ are there for you if the standard API is not
enough for your application and you want to take more control.

Starting from `Generating multisignature address`_, a tutorial follows to
show you how to use the multisignature API to execute multisig
transfers. The complete source code for the tutorial can be found `here`_.

Multisig API
------------
The multisignature API builds on top of the extended API to add multisignature
features. Just like for the regular APIs, there is both a synchronous and an
asynchronous version of the multisignature API, however, as there is no
networking required during the multisignature API calls, the difference between
them is only how you can call them.

.. py:currentmodule:: iota.multisig

Synchronous Multisignature API Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: MultisigIota


Asynchronous Multisignature API Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: AsyncMultisigIota

``create_multisig_address``
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: MultisigIota.create_multisig_address
.. automethod:: AsyncMultisigIota.create_multisig_address

``get_digests``
~~~~~~~~~~~~~~~
.. automethod:: MultisigIota.get_digests
.. automethod:: AsyncMultisigIota.get_digests

``get_private_keys``
~~~~~~~~~~~~~~~~~~~~
.. automethod:: MultisigIota.get_private_keys
.. automethod:: AsyncMultisigIota.get_private_keys

``prepare_multisig_transfer``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: MultisigIota.prepare_multisig_transfer
.. automethod:: AsyncMultisigIota.prepare_multisig_transfer

PyOTA Multisignature Types
--------------------------

There are some specific types defined in PyOTA to help you work with creating
multisignature addresses and bundles.

Multisignature Address
~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: iota.multisig.types.MultisigAddress
    :members: as_json_compatible

Multisignature ProposedBundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: iota.multisig.transaction.ProposedMultisigBundle
    :members: add_inputs

Generating multisignature address
---------------------------------

In order to use multisignature functionality, a special multisignature address
must be created. It is done by adding each key digest in agreed order into
digests list. At the end, last participant is converting digests list (Kerl
state trits) into multisignature address.

.. note::

    Each multisignature addresses participant has to create its own digest
    locally. Then, when it is created it can be safely shared with other
    participants, in order to build list of digests which then will be
    converted into multisignature address.

    Created digests should be shared with each multisignature participant, so
    each one of them could regenerate address and ensure it is OK.

Here is the example where digest is created:

.. code-block:: python

    # Create digest 3 of 3.
    api_3 =\
      MultisigIota(
        adapter = 'http://localhost:14265',

        seed =
          Seed(
            b'TESTVALUE9DONTUSEINPRODUCTION99999JYFRTI'
            b'WMKVVBAIEIYZDWLUVOYTZBKPKLLUMPDF9PPFLO9KT',
          ),
      )

    gd_result = api_3.get_digests(index=8, count=1, security_level=2)

    digest_3 = gd_result['digests'][0] # type: Digest

And here is example where digests are converted into multisignature address:

.. code-block:: python

    cma_result =\
      api_1.create_multisig_address(digests=[digest_1,
                                             digest_2,
                                             digest_3])

    # For consistency, every API command returns a dict, even if it only
    # has a single value.
    multisig_address = cma_result['address'] # type: MultisigAddress

.. note::

    As you can see in above example, multisignature addresses is created from
    list of digests, and in this case **order** is important. The same order
    need to be used in **signing transfer**.


Prepare transfer
------------------

.. note::

    Since spending tokens from the same address more than once is insecure,
    remainder should be transferred to other address. So, this address should
    be created before as next to be used multisignature address.

First signer for multisignature wallet is defining address where tokens should
be transferred and next wallet address for reminder:

.. code-block:: python

    pmt_result =\
      api_1.prepare_multisig_transfer(
        # These are the transactions that will spend the IOTAs.
        # You can divide up the IOTAs to send to multiple addresses if you
        # want, but to keep this example focused, we will only include a
        # single spend transaction.
        transfers = [
          ProposedTransaction(
            address =
              Address(
                b'TESTVALUE9DONTUSEINPRODUCTION99999NDGYBC'
                b'QZJFGGWZ9GBQFKDOLWMVILARZRHJMSYFZETZTHTZR',
              ),

            value = 42,

            # If you'd like, you may include an optional tag and/or
            # message.
            tag = Tag(b'KITTEHS'),
            message = TryteString.from_unicode('thanx fur cheezburgers'),
          ),
        ],

        # Specify our multisig address as the input for the spend
        # transaction(s).
        # Note that PyOTA currently only allows one multisig input per
        # bundle (although the protocol does not impose a limit).
        multisig_input = multisig_address,

        # If there will be change from this transaction, you MUST specify
        # the change address!  Unlike regular transfers, multisig transfers
        # will NOT automatically generate a change address; that wouldn't
        # be fair to the other participants!
        change_address = None,
      )

    prepared_trytes = pmt_result['trytes'] # type: List[TransactionTrytes]


Sign the inputs
---------------

When trytes are prepared, round of signing must be performed. Order of signing
must be the same as in generate multisignature addresses procedure (as
described above).

.. note::

    In example below, all signing is done on one local machine. In real case,
    each participant sign bundle locally and then passes it to next participant
    in previously defined order

    **index**, **count** and **security_lavel** parameters for each private key
    should be the same as used in **get_digests** function in previous steps.

.. code-block:: python

    bundle = Bundle.from_tryte_strings(prepared_trytes)

    gpk_result = api_1.get_private_keys(index=0, count=1, security_level=3)
    private_key_1 = gpk_result['keys'][0] # type: PrivateKey
    private_key_1.sign_input_transactions(bundle, 1)

    gpk_result = api_2.get_private_keys(index=42, count=1, security_level=3)
    private_key_2 = gpk_result['keys'][0] # type: PrivateKey
    private_key_2.sign_input_transactions(bundle, 4)

    gpk_result = api_3.get_private_keys(index=8, count=1, security_level=2)
    private_key_3 = gpk_result['keys'][0] # type: PrivateKey
    private_key_3.sign_input_transactions(bundle, 7)

    signed_trytes = bundle.as_tryte_strings()

.. note::

    After creation, bundle can be optionally validated:

    .. code-block:: python

        validator = BundleValidator(bundle)
        if not validator.is_valid():
          raise ValueError(
            'Bundle failed validation:\n{errors}'.format(
              errors = '\n'.join(('  - ' + e) for e in validator.errors),
            ),
          )



Broadcast the bundle
--------------------

When bundle is created it can be broadcasted in standard way:

.. code-block:: python

    api_1.send_trytes(trytes=signed_trytes, depth=3)

Remarks
-------

Full code `example`_.

.. note::

    How M-of-N works

    One of the key differences between IOTA multi-signatures is that M-of-N
    (e.g. 3 of 5) works differently. What this means is that in order to
    successfully spend inputs, all of the co-signers have to sign the transaction.
    As such, in order to enable M-of-N we have to make use of a simple trick:
    sharing of private keys.

    This concept is best explained with a concrete example:

        Lets say that we have a multi-signature between 3 parties: Alice, Bob
        and Carol. Each has their own private key, and they generated a new
        multi-signature address in the aforementioned order. Currently, this is
        a 3 of 3 multisig. This means that all 3 participants (Alice, Bob and
        Carol) need to sign the inputs with their private keys in order to
        successfully spend them.

        In order to enable a 2 of 3 multisig, the cosigners need to share their
        private keys with the other parties in such a way that no single party
        can sign inputs alone, but that still enables an M-of-N multsig. In our
        example, the sharing of the private keys would look as follows:

        Alice   ->      Bob

        Bob     ->      Carol

        Carol   ->      Alice

        Now, each participant holds two private keys that he/she can use to
        collude with another party to successfully sign the inputs and make a
        transaction. But no single party holds enough keys (3 of 3) to be able
        to independently make the transaction.

Important
---------

There are some general rules (repeated once again for convenience) which should
be followed while working with multisignature addresses (and in general with IOTA):

Signing order is important
~~~~~~~~~~~~~~~~~~~~~~~~~~

When creating a multi-signature address and when signing a transaction for that
address, it is important to follow the exact order that was used during the
initial creation. If we have a multi-signature address that was signed in the
following order: Alice -> Bob -> Carol. You will not be able to spend these
inputs if you provide the signatures in a different order
(e.g. Bob -> Alice -> Carol). As such, keep the signing order in mind.

Never re-use keys
~~~~~~~~~~~~~~~~~

Probably the most important rule to keep in mind: absolutely never re-use
private keys. IOTA uses one-time Winternitz signatures, which means that if you
re-use private keys you significantly decrease the security of your private
keys, up to the point where signing of another transaction can be done on a
conventional computer within few days. Therefore, when generating a new
multi-signature with your co-signers, always increase the private key
**index counter** and only use a single private key once. Don't use it for any
other multi-signatures and don't use it for any personal transactions.

Never share your private keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Under no circumstances - other than wanting to reduce the requirements for a
multi-signature (see section **How M-of-N works**) - should you share your
private keys. Sharing your private keys with others means that they can sign
your part of the multi-signature successfully.

.. _example: https://github.com/iotaledger/iota.py/blob/develop/examples/multisig.py
.. _wiki: https://github.com/iotaledger/wiki/blob/master/multisigs.md
.. _here: https://github.com/iotaledger/iota.py/blob/master/examples/multisig.py
