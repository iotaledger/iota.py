Generating Addresses
====================

In IOTA, addresses are generated deterministically from seeds. This
ensures that your account can be accessed from any location, as long as
you have the seed.

.. warning::
  Note that this also means that anyone with access to your seed can spend
  your iotas! Treat your seed(s) the same as you would the password for
  any other financial service.

.. note::

    PyOTA's crytpo functionality is currently very slow; on average it takes
    8-10 seconds to generate each address.

        These performance issues will be fixed in a future version of the library;
        please bear with us!

        In the meantime, you can install a C extension
        that boosts PyOTA's performance significantly (speedups of 60x are common!).

        To install the extension, run ``pip install pyota[ccurl]``.

Algorithm
---------

.. figure:: images/address_gen.svg
   :scale: 100 %
   :alt: Process of address generation in IOTA.

   Deriving addresses from a seed.

The following process takes place when you generate addresses in IOTA:

1. First, a sub-seed is derived from your seed by adding ``index`` to it,
   and hashing it once with the `Kerl`_ hash function.
2. Then the sub-seed is absorbed and squeezed in a `sponge function`_ 27 times
   for each security level. The result is a private key that varies in length
   depending on security level.

   .. note::
     A private key with ``security_level = 1`` consists of 2187 trytes, which is
     exactly 27 x 81 trytes. As the security level increases, so does the length
     of the private key: 2 x 2187 trytes for ``security_level = 2``, and 3 x 2187
     trytes for ``security_level = 3``.

3. A private key is split into 81-tryte segments, and these segments are hashed
   26 times. A group of 27 hashed segments is called a key fragment. Observe,
   that a private key has one key fragment for each security level.
4. Each key fragment is hashed once more to generate key digests, that are
   combined and hashed once more to get the 81-tryte address.

   .. note::
     An address is the public key pair of the corresponding private key. When
     you spend iotas from an address, you need to sign the transaction with a
     key digest that was generated from the address's corresponing private key.
     This way you prove that you own the funds on that address.

PyOTA provides two methods for generating addresses:

Using the API
-------------

.. code:: python

    from iota import Iota

    api = Iota('http://localhost:14265', b'SEED9GOES9HERE')

    # Generate 5 addresses, starting with index 0.
    gna_result = api.get_new_addresses(count=5)
    # Result is a dict that contains a list of addresses.
    addresses = gna_result['addresses']

    # Generate 1 address, starting with index 42:
    gna_result = api.get_new_addresses(index=42)
    addresses = gna_result['addresses']

    # Find the first unused address, starting with index 86:
    gna_result = api.get_new_addresses(index=86, count=None)
    addresses = gna_result['addresses']

To generate addresses using the API, invoke its :py:meth:`iota.Iota.get_new_addresses`
method, using the following parameters:

-  ``index: int``: The starting index (defaults to 0). This can be used
   to skip over addresses that have already been generated.
-  ``count: Optional[int]``: The number of addresses to generate
   (defaults to 1).

    - If ``None``, the API will generate addresses until it finds one that
      has not been used (has no transactions associated with it on the
      Tangle and was never spent from). It will then return the unused address
      and discard the rest.
-  ``security_level: int``: Determines the security level of the
   generated addresses. See `Security Levels <#security-levels>`__
   below.

Depending on the ``count`` parameter, :py:meth:`Iota.get_new_addresses` can be
operated in two modes.

Offline mode
~~~~~~~~~~~~

  When ``count`` is greater than 0, the API generates ``count`` number of
  addresses starting from ``index``. It does not check the Tangle if
  addresses were used or spent from before.

Online mode
~~~~~~~~~~~

  When ``count`` is ``None``, the API starts generating addresses starting
  from ``index``. Then, for each generated address, it checks the Tangle
  if the address has any transactions associated with it, or if the address
  was ever spent from. If both of the former checks return "no", address
  generation stops and the address is returned (a new address is found).

.. warning::
    Take care when using the online mode after a snapshot. Transactions referencing
    a generated address may have been pruned from a node's ledger, therefore the
    API could return an already-used address as "new" (note: The snapshot has
    no effect on the "was ever spent from" check).

    To make your application more robust to handle snapshots, it is recommended
    that you keep a local database with at least the indices of your used addresses.
    After a snapshot, you could specify ``index`` parameter as the last
    index in your local used addresses database, and keep on generating truly
    new addresses.

    PyOTA is planned to receive the `account module`_ in the future, that makes
    the library stateful and hence would solve the issue mentioned above.

Using AddressGenerator
----------------------

.. code:: python

    from iota.crypto.addresses import AddressGenerator

    generator = AddressGenerator(b'SEED9GOES9HERE')

    # Generate a list of addresses:
    addresses = generator.get_addresses(start=0, count=5)

    # Generate a list of addresses in reverse order:
    addresses = generator.get_addresses(start=42, count=10, step=-1)

    # Create an iterator, advancing 5 indices each iteration.
    iterator = generator.create_iterator(start=86, step=5)
    for address in iterator:
      ...

If you want more control over how addresses are generated, you can use
:py:class:`iota.crypto.addresses.AddressGenerator`.

``AddressGenerator`` can create iterators, allowing your application to
generate addresses as needed, instead of having to generate lots of
addresses up front.

You can also specify an optional ``step`` parameter, which allows you to
skip over multiple addresses between iterations... or even iterate over
addresses in reverse order!

AddressGenerator
~~~~~~~~~~~~~~~~

.. autoclass:: iota.crypto.addresses.AddressGenerator

**get_addresses**
^^^^^^^^^^^^^^^^^

.. automethod:: iota.crypto.addresses.AddressGenerator.get_addresses

**create_iterator**
^^^^^^^^^^^^^^^^^^^

.. automethod:: iota.crypto.addresses.AddressGenerator.create_iterator

Security Levels
---------------

.. code:: python

    gna_result = api.get_new_addresses(security_level=3)

    generator =\
      AddressGenerator(
        seed = b'SEED9GOES9HERE',
        security_level = 3,
      )

If desired, you may change the number of iterations that
:py:class:`iota.crypto.addresses.AddressGenerator` or
:py:class:`iota.Iota.get_new_addresses` uses internally when generating new
addresses, by specifying a different ``security_level`` when creating a new
instance.

``security_level`` should be between 1 and 3, inclusive. Values outside
this range are not supported by the IOTA protocol.

Use the following guide when deciding which security level to use:

-  ``security_level=1``: Least secure, but generates addresses the
   fastest.
-  ``security_level=2``: Default; good compromise between speed and
   security.
-  ``security_level=3``: Most secure; results in longer signatures in
   transactions.

.. _Kerl: https://github.com/iotaledger/kerl
.. _sponge function: https://keccak.team/sponge_duplex.html
.. _account module: https://docs.iota.org/docs/client-libraries/0.1/account-module/introduction/overview