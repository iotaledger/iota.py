.. image:: https://travis-ci.org/iotaledger/iota.lib.py.svg?branch=develop
   :target: https://travis-ci.org/iotaledger/iota.lib.py

=====
PyOTA
=====
This is the official Python library for the IOTA Core.

It implements both the `official API`_, as well as newly-proposed functionality
(such as signing, bundles, utilities and conversion).

Join the Discussion
===================
If you want to get involved in the community, need help with getting setup,
have any issues related with the library or just want to discuss Blockchain,
Distributed Ledgers and IoT with other people, feel free to join our `Slack`_.

You can also ask questions on our `dedicated forum`_.

If you encounter any issues while using PyOTA, please report them using the
`PyOTA Bug Tracker`_.

============
Dependencies
============
PyOTA is compatible with Python 3.6, 3.5 and 2.7.

============
Installation
============
To install the latest version::

  pip install pyota

Optional C Extension
====================
PyOTA has an optional C extension that improves the performance of its
cryptography features significantly.

To install this **experimental** extension, use the following command::

   pip install pyota[ccurl]

.. DANGER::
   **THE C EXTENSION IS EXPERIMENTAL AND HAS NOT BEEN VETTED FOR**
   **STABILITY/SECURITY YET; DO NOT USE IN PRODUCTION CODE!!!**

Installing from Source
======================

1. `Create virtualenv`_ (recommended, but not required).
2. ``git clone https://github.com/iotaledger/iota.lib.py.git``
3. ``pip install -e .``

Running Unit Tests
------------------
To run unit tests after installing from source::

  python setup.py test

PyOTA is also compatible with `tox`_::

  pip install tox
  tox

=============
Documentation
=============
For the full documentation of this library, please refer to the
`official API`_


.. _Create virtualenv: https://virtualenvwrapper.readthedocs.io/
.. _PyOTA Bug Tracker: https://github.com/iotaledger/iota.lib.py/issues
.. _Slack: http://slack.iotatoken.com/
.. _dedicated forum: https://forum.iotatoken.com/
.. _official API: https://iota.readme.io/
.. _tox: https://tox.readthedocs.io/
