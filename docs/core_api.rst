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

.. py:currentmodule:: iota

``add_neighbors``
-----------------
.. automethod:: Iota.add_neighbors

``attach_to_tangle``
--------------------
.. automethod:: Iota.attach_to_tangle

``broadcast_transactions``
--------------------------
.. automethod:: Iota.broadcast_transactions

``check_consistency``
---------------------
.. automethod:: Iota.check_consistency

``find_transactions``
---------------------
.. automethod:: Iota.find_transactions

``get_balances``
----------------
.. automethod:: Iota.get_balances

``get_inclusion_states``
------------------------
.. automethod:: Iota.get_inclusion_states

``get_missing_transactions``
----------------------------
.. automethod:: Iota.get_missing_transactions

``get_neighbors``
-----------------
.. automethod:: Iota.get_neighbors

``get_node_api_configuration``
------------------------------
.. automethod:: Iota.get_node_api_configuration

``get_node_info``
-----------------
.. automethod:: Iota.get_node_info

``get_tips``
------------
.. automethod:: Iota.get_tips

``get_transactions_to_approve``
-------------------------------
.. automethod:: Iota.get_transactions_to_approve

``get_trytes``
--------------
.. automethod:: Iota.get_trytes

``interrupt_attaching_to_tangle``
---------------------------------
.. automethod:: Iota.interrupt_attaching_to_tangle

``remove_neighbors``
--------------------
.. automethod:: Iota.remove_neighbors

``store_transactions``
----------------------
.. automethod:: Iota.store_transactions

``were_addresses_spent_from``
-----------------------------
.. automethod:: Iota.were_addresses_spent_from