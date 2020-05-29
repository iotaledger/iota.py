Extended API Methods
====================

The Extended API includes a number of "high level" commands to perform
tasks such as sending and receiving transfers.

.. note::
    Below you will find the documentation for both the synchronous and
    asynchronous versions of the Extebded API methods.

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

``broadcast_and_store``
-----------------------
.. automethod:: Iota.broadcast_and_store
.. automethod:: AsyncIota.broadcast_and_store

``broadcast_bundle``
--------------------
.. automethod:: Iota.broadcast_bundle
.. automethod:: AsyncIota.broadcast_bundle

``find_transaction_objects``
----------------------------
.. automethod:: Iota.find_transaction_objects
.. automethod:: AsyncIota.find_transaction_objects

``get_account_data``
--------------------
.. automethod:: Iota.get_account_data
.. automethod:: AsyncIota.get_account_data

``get_bundles``
---------------
.. automethod:: Iota.get_bundles
.. automethod:: AsyncIota.get_bundles

``get_inputs``
--------------
.. automethod:: Iota.get_inputs
.. automethod:: AsyncIota.get_inputs

``get_new_addresses``
---------------------
.. automethod:: Iota.get_new_addresses
.. automethod:: AsyncIota.get_new_addresses

``get_transaction_objects``
---------------------------
.. automethod:: Iota.get_transaction_objects
.. automethod:: AsyncIota.get_transaction_objects

``get_transfers``
-----------------
.. automethod:: Iota.get_transfers
.. automethod:: AsyncIota.get_transfers

``is_promotable``
-----------------
.. automethod:: Iota.is_promotable
.. automethod:: AsyncIota.is_promotable

``is_reattachable``
-------------------
.. automethod:: Iota.is_reattachable
.. automethod:: AsyncIota.is_reattachable

``prepare_transfer``
--------------------
.. automethod:: Iota.prepare_transfer
.. automethod:: AsyncIota.prepare_transfer

``promote_transaction``
-----------------------
.. automethod:: Iota.promote_transaction
.. automethod:: AsyncIota.promote_transaction

``replay_bundle``
-----------------
.. automethod:: Iota.replay_bundle
.. automethod:: AsyncIota.replay_bundle

``send_transfer``
-----------------
.. automethod:: Iota.send_transfer
.. automethod:: AsyncIota.send_transfer

``send_trytes``
---------------
.. automethod:: Iota.send_trytes
.. automethod:: AsyncIota.send_trytes

``traverse_bundle``
-------------------
.. automethod:: Iota.traverse_bundle
.. automethod:: AsyncIota.traverse_bundle

.. _Python coroutines: https://docs.python.org/3/library/asyncio-task.html
.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _this article: https://realpython.com/async-io-python/