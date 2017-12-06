Multisignature
==============

Multisignature transactions are transactions which require multiple signatures before execution. In simplest example it means that, if there is token wallet which require 5 signatures from different parties, all 5 parties must sign spent transaction, before it will be processed. 

It is standard functionality in blockchain systems and it is also implemented in IOTA

.. note::

    You can read more about IOTA multisignature on the `wiki`_.  

Generating multisignature address
---------------------------------

In order to use multisignature functionality, a special multisignature address must be created. It is done by adding each key digest in agreed order into digests list. At the end, last participant is converting digests list (Curl state trits) into multisignature address. 

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



Prepare transfer
------------------

.. note::

    Since spending tokens from the same address more than once is insecure, remainder should be transferred to other address. So, this address should be created before as next to be used multisignature address.

First signer for multisignature wallet is defining address where tokens should be transferred and next wallet address for reminder:

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
            message = TryteString.from_string('thanx fur cheezburgers'),
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

.. note::

    Validate the signatures.

Broadcast the bundle
--------------------

Remarks
-------

Full code `example`_.

.. note::

    How M-of-N works

.. _example: https://github.com/iotaledger/iota.lib.py/blob/develop/examples/multisig.py
.. _wiki: https://github.com/iotaledger/wiki/blob/master/multisigs.md
