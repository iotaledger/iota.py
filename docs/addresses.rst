Generating Addresses
====================

In IOTA, addresses are generated deterministically from seeds. This
ensures that your account can be accessed from any location, as long as
you have the seed.

Note that this also means that anyone with access to your seed can spend
your IOTAs! Treat your seed(s) the same as you would the password for
any other financial service.

.. note::

    PyOTA's crytpo functionality is currently very slow; on average it takes
    8-10 seconds to generate each address.

        These performance issues will be fixed in a future version of the library;
        please bear with us!

        In the meantime, if you are using Python 3, you can install a C extension
        that boosts PyOTA's performance significantly (speedups of 60x are common!).

        To install the extension, run ``pip install pyota[ccurl]``.

        **Important:** The extension is not yet compatible with Python 2.

        If you are familiar with Python 2's C API, we'd love to hear from you!
        Check the `GitHub issue <https://github.com/todofixthis/pyota-ccurl/issues/4>`_
        for more information.

PyOTA provides two methods for generating addresses:

Using the API
-------------

.. code:: python

    from iota import Iota

    api = Iota('http://localhost:14265', b'SEED9GOES9HERE')

    # Generate 5 addresses, starting with index 0.
    gna_result = api.get_new_addresses(count=5)
    addresses = gna_result['addresses']

    # Generate 1 address, starting with index 42:
    gna_result = api.get_new_addresses(start=42)
    addresses = gna_result['addresses']

    # Find the first unused address, starting with index 86:
    gna_result = api.get_new_addresses(start=86, count=None)
    addresses = gna_result['addresses']

To generate addresses using the API, invoke its ``get_new_addresses``
method, using the following parameters:

-  ``start: int``: The starting index (defaults to 0). This can be used
   to skip over addresses that have already been generated.
-  ``count: Optional[int]``: The number of addresses to generate
   (defaults to 1).
-  If ``None``, the API will generate addresses until it finds one that
   has not been used (has no transactions associated with it on the
   Tangle). It will then return the unused address and discard the rest.
-  ``security_level: int``: Determines the security level of the
   generated addresses. See `Security Levels <#security-levels>`__
   below.

``get_new_addresses`` returns a dict with the following items:

-  ``addresses: List[Address]``: The generated address(es). Note that
   this value is always a list, even if only one address was generated.

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
the ``AddressGenerator`` class.

``AddressGenerator`` can create iterators, allowing your application to
generate addresses as needed, instead of having to generate lots of
addresses up front.

You can also specify an optional ``step`` parameter, which allows you to
skip over multiple addresses between iterations... or even iterate over
addresses in reverse order!

``AddressGenerator`` provides two methods:

-  ``get_addresses: (int, int, int) -> List[Address]``: Returns a list
   of addresses. This is the same method that the ``get_new_addresses``
   API command uses internally.
-  ``create_iterator: (int, int) -> Generator[Address]``: Returns an
   iterator that will create addresses endlessly. Use this if you have a
   feature that needs to generate addresses "on demand".

Security Levels
===============

.. code:: python

    gna_result = api.get_new_addresses(security_level=3)

    generator =\
      AddressGenerator(
        seed = b'SEED9GOES9HERE',
        security_level = 3,
      )

If desired, you may change the number of iterations that
``AddressGenerator`` uses internally when generating new addresses, by
specifying a different ``security_level`` when creating a new instance.

``security_level`` should be between 1 and 3, inclusive. Values outside
this range are not supported by the IOTA protocol.

Use the following guide when deciding which security level to use:

-  ``security_level=1``: Least secure, but generates addresses the
   fastest.
-  ``security_level=2``: Default; good compromise between speed and
   security.
-  ``security_level=3``: Most secure; results in longer signatures in
   transactions.
