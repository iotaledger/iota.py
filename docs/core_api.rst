Core API Methods
================

The Core API includes all of the core API calls that are made
available by the current `IOTA Reference
Implementation <https://github.com/iotaledger/iri>`__.

These methods are "low level" and generally do not need to be called
directly.

For the full documentation of all the Core API calls, please refer
to the `official documentation <https://docs.iota.org/docs/node-software/0.1/
iri/references/api-reference>`__.

.. note::
    Below you will find the documentation for both the synchronous and
    asynchronous versions of the Core API methods.

    It should be made clear, that they do exactly the same IOTA related
    operations, accept the same arguments and return the same structures.
    Asynchronous API calls are non-blocking, so your application
    can do other stuff while waiting for the result from the network.

    While synchronous API calls are regular Python methods, their respective
    asynchronous versions are `Python coroutines`_. You can ``await`` their
    results, schedule them for execution inside and event loop and much more.
    PyOTA uses the built-in `asyncio`_ Python module for asynchronous operation.
    For an overview of what you can do with it, head over to `this article`_.

.. py:currentmodule:: iota

``add_neighbors``
-----------------
.. automethod:: Iota.add_neighbors
.. automethod:: AsyncIota.add_neighbors

``attach_to_tangle``
--------------------
.. automethod:: Iota.attach_to_tangle
.. automethod:: AsyncIota.attach_to_tangle

``broadcast_transactions``
--------------------------
.. automethod:: Iota.broadcast_transactions
.. automethod:: AsyncIota.broadcast_transactions

``check_consistency``
---------------------
.. automethod:: Iota.check_consistency
.. automethod:: AsyncIota.check_consistency

``find_transactions``
---------------------
.. automethod:: Iota.find_transactions
.. automethod:: AsyncIota.find_transactions

``get_balances``
----------------
.. automethod:: Iota.get_balances
.. automethod:: AsyncIota.get_balances

``get_inclusion_states``
------------------------
.. automethod:: Iota.get_inclusion_states
.. automethod:: AsyncIota.get_inclusion_states

``get_missing_transactions``
----------------------------
.. automethod:: Iota.get_missing_transactions
.. automethod:: AsyncIota.get_missing_transactions

``get_neighbors``
-----------------
.. automethod:: Iota.get_neighbors
.. automethod:: AsyncIota.get_neighbors

``get_node_api_configuration``
------------------------------
.. automethod:: Iota.get_node_api_configuration
.. automethod:: AsyncIota.get_node_api_configuration

``get_node_info``
-----------------
.. automethod:: Iota.get_node_info
.. automethod:: AsyncIota.get_node_info

``get_transactions_to_approve``
-------------------------------
.. automethod:: Iota.get_transactions_to_approve
.. automethod:: AsyncIota.get_transactions_to_approve

``get_trytes``
--------------
.. automethod:: Iota.get_trytes
.. automethod:: AsyncIota.get_trytes

``interrupt_attaching_to_tangle``
---------------------------------
.. automethod:: Iota.interrupt_attaching_to_tangle
.. automethod:: AsyncIota.interrupt_attaching_to_tangle

``remove_neighbors``
--------------------
.. automethod:: Iota.remove_neighbors
.. automethod:: AsyncIota.remove_neighbors

``store_transactions``
----------------------
.. automethod:: Iota.store_transactions
.. automethod:: AsyncIota.store_transactions

``were_addresses_spent_from``
-----------------------------
.. automethod:: Iota.were_addresses_spent_from
.. automethod:: AsyncIota.were_addresses_spent_from

.. _Python coroutines: https://docs.python.org/3/library/asyncio-task.html
.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _this article: https://realpython.com/async-io-python/